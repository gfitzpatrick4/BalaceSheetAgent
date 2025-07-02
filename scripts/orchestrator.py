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


sys.path.extend(['//fs1/dept/trading/specialsituations/Working/MARIO/SEC/scripts/'])

from openai.types import VectorStore
from agents import set_default_openai_key, set_tracing_export_api_key, trace
from agents import Agent, Runner, ModelSettings, FileSearchTool

#from agents import Runner          # your wrapper
from EdgarCache.Client.Client import Client as EdgarCacheClient
from EdgarCache.Sec.Util import Util
from EdgarCache.Sec.Submissions import Submission, Submissions

from tqdm.auto import tqdm

from models import FullBalanceSheet
from tools  import extract_doc_urls, create_vector_store, make_file_search_tool
from my_agents import (                     # imported from package
    make_assets_agent,
    make_liabilities_agent,
    make_equity_agent,
    make_assembler_agent,
    make_expander_agent
)


async def build_balance_sheet(
        cik: int | str,
        index_url: str,
        ec: EdgarCacheClient,
        openai_client=None
) -> FullBalanceSheet:
    """
    Main entry-point called by CLI / notebooks.

    Returns a validated FullBalanceSheet object.
    """


    doc_urls = [url for url in Util.GetRelatedUrls(str(ec.Get(index_url).content).replace("/ix?doc=",""))]

    # 2. Vector store (group all docs under one store)
    vs = create_vector_store(ec, name=f"{cik}_10Q_vector", urls=doc_urls,
                             client=openai_client)

    tool = make_file_search_tool(vs.id, max_k=12)

    # 3. Instantiate agents (each factory just builds an Agent object + prompt)
    assets_agent      = make_assets_agent(tool)
    liabilities_agent = make_liabilities_agent(tool)
    equity_agent      = make_equity_agent(tool)
    assembler_agent   = make_assembler_agent()      # no tool needed

    prompt = "Return the most recent balance sheet."

    # 4. Run the three section agents in parallel
    async with asyncio.TaskGroup() as tg:
        t_assets      = tg.create_task(Runner.run(assets_agent,      prompt))
        t_liabilities = tg.create_task(Runner.run(liabilities_agent, prompt))
        t_equity      = tg.create_task(Runner.run(equity_agent,      prompt))

    assets_tbl      = t_assets.result().final_output
    liabilities_tbl = t_liabilities.result().final_output
    equity_tbl      = t_equity.result().final_output


    expander = make_expander_agent(tool)

    async with asyncio.TaskGroup() as tg:
        ta = tg.create_task(Runner.run(expander, assets_tbl.model_dump_json()))
        tl = tg.create_task(Runner.run(expander, liabilities_tbl.model_dump_json()))
        te = tg.create_task(Runner.run(expander, equity_tbl.model_dump_json()))

    assets_tbl      = (await ta).final_output
    liabilities_tbl = (await tl).final_output
    equity_tbl      = (await te).final_output

    # 5. Assemble
    
    assembler_payload ={
            "company_name": None,     # can be parsed from index_html if needed
            "cik":          str(cik),
            "filing_date":  None,
            "period_end":   None,
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

    # 6. Optional: delete vector store to save quota
    # openai_client.vector_stores.delete(vs.id)

    return full_bs