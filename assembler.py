# balancesheet/agents/assembler_agent.py
from agents import Agent, ModelSettings
from models import FullBalanceSheet

_ASSEMBLER_PROMPT = """
You will receive:
    - company_name (str)
    - cik (str)
    - filing_date (str)
    - period_end (str | null)
    - assets_table      (JSON matching SectionTable)
    - liabilities_table (JSON matching SectionTable)
    - equity_table      (JSON matching SectionTable)

Merge them into ONE FullBalanceSheet JSON object.
Keep every numeric value exactly as supplied.

After building:
• If Assets total ≠ Liabilities total + Equity total by more than $0.01
  insert an extra line in the *equity* section:
       line_item = "Imbalance detected"
       value     = Assets total − (Liab+Equity)
  and continue.

Return ONLY valid JSON.
"""

def make_assembler_agent() -> Agent:
    return Agent(
        name          = "BalanceSheetAssembler",
        model         = 'o3',
        #model_settings= ModelSettings(temperature=0),
        output_type   = FullBalanceSheet,
        instructions  = _ASSEMBLER_PROMPT
    )