from __future__ import annotations

from agents import Agent, ModelSettings
from models import BalanceSheetDeltaList


_PROMPT = """
You are a CPA-level accountant. You will receive a JSON object matching UpdateSummary.
For each FilingChange, read the `update_log` description and create a balanced BalanceSheetDelta reflecting how the balance sheet changes.
Balance the delta so that Assets change equals Liabilities plus Equity change.
Each BalanceSheetDelta has three lists: `assets`, `liabilities` and `equity`.  Each list contains DeltaEntry objects with keys `line_item` and `value`.

The accountant agents job is for each update log contained in a filing change, translate the summary
into a quanitative change. Meaning, determine which line item is first directly changed by the event (Company A issues
100,000 shares of common stock at $10 per share -> Cash + 1,000,000), and then the equivalent line item that needs to change
to balance this update (Common stock increases by par value and APIC increases by the difference between the issue price and 
the par value --> Common Stock + $1,000 and APIC + $999,000). In terms of what this should look like in terms of data structure,
here is what is would look like for this example:

BS DELTA = { 'assets' : [
							{Cash : 1000000}
						],
			'liabilites' : [
								{"":""}
							],
			'equity' : [
							{Common Stock : 1000},
							{Additional paid-in capital : 999000}
						]
			}

It is imperative that a BalanceSheetDelta object is balanced itself. Meaning Cash (1,000,000) = Common Stock (1,000)
+ APIC (999,000)

Lets say Company A purchases 1,500 Bitcoin for $60K. The BS Delta of that change would look like this (figures wrapped
in () are negative):

BS DELTA = { 'assets' : [
							{Cash : (90000000)},
							{Digital Assets : 90000000}
						],
			'liabilites' : [
								{"":""}
							],
			'equity' : [
							{"":""}
						]
			}




Return the list of BalanceSheetDelta objects in the same order as the input events, wrapped in a JSON object with key `deltas` matching BalanceSheetDeltaList.
Each delta should reference the same units (USD) as the update_log amounts.
Return ONLY valid JSON conforming to BalanceSheetDeltaList.
"""


def make_accountant_agent(tool) -> Agent:
    return Agent(
        name="AccountantAgent",
        model="o3",
        model_settings=ModelSettings(reasoning={'effort': 'high'}),
        output_type=BalanceSheetDeltaList,
        instructions=_PROMPT,
        tools=[tool],
    )
