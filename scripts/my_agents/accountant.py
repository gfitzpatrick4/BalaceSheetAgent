from __future__ import annotations

from agents import Agent, ModelSettings
from models import BalanceSheetDeltaList


_PROMPT = """
You are a CPA-level accountant. You will receive a JSON object matching UpdateSummary.
For each FilingChange, read the `update_log` description and create a balanced BalanceSheetDelta reflecting how the balance sheet changes.
Balance the delta so that Assets change equals Liabilities plus Equity change.
Return the list of BalanceSheetDelta objects in the same order as the input events, wrapped in a JSON object with key `deltas` matching BalanceSheetDeltaList.
Each delta should reference the same units (USD) as the update_log amounts.
Return ONLY valid JSON conforming to BalanceSheetDeltaList.
"""


def make_accountant_agent(tool=None) -> Agent:
    return Agent(
        name="AccountantAgent",
        model="o3",
        model_settings=ModelSettings(reasoning={'effort': 'high'}),
        output_type=BalanceSheetDeltaList,
        instructions=_PROMPT,
        tools=[tool] if tool else [],
    )
