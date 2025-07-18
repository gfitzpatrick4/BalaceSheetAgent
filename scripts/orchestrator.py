from __future__ import annotations
'''
 Does: vector store creation → instantiate 3 sub-agents → run concurrently
→ pass output to assembler → return FullBalanceSheet.


'''

# balancesheet/orchestrator.py
"""
High-level workflow:
    1. Download & parse SEC index page
    2. Create vector store
    3. Spin up three section agents + assembler
    4. Return FullBalanceSheet
"""



import asyncio
from typing import Dict

import sys
import os
import inspect
from bs4 import BeautifulSoup
import pprint as pprint
import json
import time
import math
from tqdm.auto import tqdm


sys.path.extend(['//fs1/dept/trading/specialsituations/Working/MARIO/SEC/scripts/'])

from openai.types import VectorStore
from agents import set_default_openai_key, set_tracing_export_api_key, trace
from agents import Agent, Runner, ModelSettings, FileSearchTool

#from agents import Runner          # your wrapper
from EdgarCache.Client.Client import Client as EdgarCacheClient
from EdgarCache.Sec.Util import Util
from EdgarCache.Sec.Submissions import Submission, Submissions
from SEC_utils import SubmissionPage # type: ignore
from datetime import datetime as dt

from tqdm.auto import tqdm

from models import FullBalanceSheet, UpdateSummary, BalanceSheetDeltaList
from tools  import extract_doc_urls, create_vector_store, make_file_search_tool, get_all_sub_filings, create_vector_store_for_updates
from apply_updates import  apply_updates
from my_agents import (                     # imported from package
    make_assets_agent,
    make_liabilities_agent,
    make_equity_agent,
    make_assembler_agent,
    make_expander_agent,
    make_update_agent,
    make_accountant_agent
)


async def build_balance_sheet(
        cik: int | str,
        index_url: str,
        ec: EdgarCacheClient,
        openai_client=None
) -> tuple[FullBalanceSheet, FullBalanceSheet]:
    """
    Main entry-point called by CLI / notebooks.

    Returns both the fully expanded balance sheet from the filing and the
    pro forma balance sheet with subsequent updates applied.
    """
    start_program = time.perf_counter()
    page = SubmissionPage(edgarCache=ec,url=index_url)
    filingDate = f"{page.metadata.get('Filing Date'):%Y-%m-%d}"
    if page.filers:
        first = page.filers[0]
        if isinstance(first, dict):
            name = first.get('name') or first.get('company_name')
        else:
            name = getattr(first, "company_name", None) or getattr(first, "name", None)
    else:
        name = None
    if not name:
        name = str(cik)
    period = f"{page.metadata.get('Period of Report'):%Y-%m-%d}"

    doc_urls = [url for url in Util.GetRelatedUrls(str(ec.Get(index_url).content).replace("/ix?doc=",""))]

    pbar = tqdm(total=9, desc="Build balance sheet")

    # 2. Vector store (group all docs under one store)
    start_vs = time.perf_counter()
    vs = create_vector_store(ec, name=f"{cik}_10Q_vector", urls=doc_urls,
                             client=openai_client)
    vs_elapsed = time.perf_counter() - start_vs
    pbar.write(f"Vector store creation took {vs_elapsed:.2f}s")
    
    pbar.update(1)

    agents_start = time.perf_counter()
    tool = make_file_search_tool(vs.id, max_k=12)

    # 3. Instantiate agents (each factory just builds an Agent object + prompt)
    assets_agent      = make_assets_agent(tool)
    liabilities_agent = make_liabilities_agent(tool)
    equity_agent      = make_equity_agent(tool)
    assembler_agent   = make_assembler_agent()      # no tool needed

    prompt = "Return the most recent balance sheet."
    agents_elapsed = time.perf_counter() - agents_start
    pbar.write(f"Section agent creation took {agents_elapsed:.2f}s")
    pbar.update(1)

    # 4. Run the three section agents in parallel
    start_sections = time.perf_counter()
    async with asyncio.TaskGroup() as tg:
        t_assets      = tg.create_task(Runner.run(assets_agent,      prompt))
        t_liabilities = tg.create_task(Runner.run(liabilities_agent, prompt))
        t_equity      = tg.create_task(Runner.run(equity_agent,      prompt))

    assets_tbl      = t_assets.result().final_output
    liabilities_tbl = t_liabilities.result().final_output
    equity_tbl      = t_equity.result().final_output

    sections_elapsed = time.perf_counter() - start_sections
    pbar.write(f"Section agents took {sections_elapsed:.2f}s")

    pbar.update(1)
    """
    expander = make_expander_agent(tool)

    start_expand = time.perf_counter()
    async with asyncio.TaskGroup() as tg:
        ta = tg.create_task(Runner.run(expander, assets_tbl.model_dump_json()))
        tl = tg.create_task(Runner.run(expander, liabilities_tbl.model_dump_json()))
        te = tg.create_task(Runner.run(expander, equity_tbl.model_dump_json()))

    assets_tbl      = (await ta).final_output
    liabilities_tbl = (await tl).final_output
    equity_tbl      = (await te).final_output

    expand_elapsed = time.perf_counter() - start_expand
    pbar.write(f"Expander agents took {expand_elapsed:.2f}s")
    """
    pbar.update(1)
    
    # 5. Assemble
    
    assembler_payload ={
            "company_name": name,     # can be parsed from index_html if needed
            "cik":          str(cik),
            "filing_date":  filingDate,
            "period_end":   period,
            "assets_table":      assets_tbl.model_dump(),
            "liabilities_table": liabilities_tbl.model_dump(),
            "equity_table":      equity_tbl.model_dump()
        }

    assembled = await Runner.run(
        assembler_agent,
        [
            {"role":"user", "content": json.dumps(assembler_payload)}
        ]
    )



    full_bs = assembled.final_output
    pbar.update(1)

    format_string = "%Y,%m,%d"
    
    sub_urls_index = get_all_sub_filings(ec, cik,dt.strptime(f'{page.metadata.get("Filing Date"):%Y,%m,%d}',format_string).date())
    sub_urls = []
    for url in sub_urls_index:
        sub_urls.append([u for u in Util.GetRelatedUrls(str(ec.Get(url).content).replace("/ix?doc=",""))])

    start_updates_vs = time.perf_counter()
    
    vs_updates = create_vector_store_for_updates(ec, name=f"{cik}_updates_vector", urls=sub_urls,
                                                  client=openai_client)
    
    updates_vs_elapsed = time.perf_counter() - start_updates_vs
    pbar.write(f"Updates vector store creation took {updates_vs_elapsed:.2f}s")

    pbar.update(1)

    tool_updates = make_file_search_tool(vs_updates.id, max_k=12)
    update_agent = make_update_agent(tool_updates)
    accountant_agent = make_accountant_agent(tool_updates)

    pbar.update(1)

    start_update_agents = time.perf_counter()
    async with asyncio.TaskGroup() as tg:
        t_updates = tg.create_task(
            Runner.run(update_agent, full_bs.model_dump_json())
        )

    updates: UpdateSummary = (await t_updates).final_output
    update_agents_elapsed = time.perf_counter() - start_update_agents
    pbar.write(f"Update Agent run took {update_agents_elapsed:.2f}s")
    accountant_resp = await Runner.run(accountant_agent, updates.model_dump_json())
    delta_list: BalanceSheetDeltaList = accountant_resp.final_output

    for ch, delta in zip(updates.changes, delta_list.deltas):
        ch.delta = delta

    
    start_apply = time.perf_counter()
    updated_bs = await apply_updates(full_bs, updates)
    apply_elapsed = time.perf_counter() - start_apply
    pbar.write(f"Applying updates took {apply_elapsed:.2f}s")

    pbar.update(1)

    total_elapsed = time.perf_counter() - start_program
    pbar.write(f"The entire program took {math.floor(total_elapsed/60)} min and {total_elapsed%60:.2f}s")

    return full_bs, updated_bs