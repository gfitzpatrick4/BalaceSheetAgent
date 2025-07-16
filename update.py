from __future__ import annotations

from agents import Agent, ModelSettings
from models import UpdateSummary
from datetime import datetime as dt


def make_update_agent(tool) -> Agent:
    return Agent(
        name="BalanceSheetUpdater",
        model="o3",
        model_settings=ModelSettings(reasoning={'effort':'high'}),
        output_type=UpdateSummary,
        instructions=_PROMPT,
        tools=[tool],
    )


_PROMPT = f"""
You are a CPA-level financial-statement analyst. Today is {dt.today()}. You will receive:
1. The most recent FullBalanceSheet JSON extracted from a filing.
2. The filing text via FileSearchTool.
3. The full text of all subsequent filings via FileSearchTool.

Scan the original filing and the subsequent filings for settled events that change the balance sheet (e.g. stock issuances, debt repayments, acquisitions).  Ignore pending or proposed transactions.
For each settled event record:
  - the effective date,
  - a short update_log describing what happened and the numeric amounts involved,
  - a citation describing which filing and location the data came from.

Also determine the exact numbers of common and preferred shares currently outstanding based solely on these filings.

Return a JSON object matching UpdateSummary with:
  changes: ordered list of events as described above
  total_common_shares: integer count of common shares outstanding
  total_preferred_shares: integer count of preferred shares outstanding

Return ONLY valid JSON conforming to UpdateSummary. Each FilingChange must include ``update_log`` and ``citation``.
Do not attempt to update the balance sheet yourself.
"""


