from __future__ import annotations

from agents import Agent, ModelSettings
from models import UpdateSummary, FilingChange
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


def make_fix_agent(tool) -> Agent:
    """Agent that receives a balance sheet and an unbalanced FilingChange and returns a corrected FilingChange."""
    return Agent(
        name="UpdateFixer",
        model="o3",
        model_settings=ModelSettings(reasoning={'effort':'high'}),
        output_type=FilingChange,
        instructions=_FIX_PROMPT,
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
  - each balance-sheet line affected with its numeric change (positive or negative) and section name,
  - a citation describing which filing and location the data came from.

Also determine the exact numbers of common and preferred shares currently outstanding based solely on these filings.

Return a JSON object matching UpdateSummary with:
  changes: ordered list of events as described above
  total_common_shares: integer count of common shares outstanding
  total_preferred_shares: integer count of preferred shares outstanding

Return ONLY valid JSON conforming to UpdateSummary. Do not attempt to update the balance sheet yourself.
"""


_FIX_PROMPT = f"""
You are a CPA-level financial-statement analyst. You will receive:
1. A FullBalanceSheet JSON representing the balance sheet before an update.
2. A FilingChange JSON representing the proposed update.

Applying this change caused the balance sheet to be unbalanced. Double-check the referenced filings via FileSearchTool and 
return a corrected FilingChange whose deltas will balance the sheet. If no corrected values can be found, return the original FilingChange unchanged.

Return ONLY a valid FilingChange JSON object.
"""
