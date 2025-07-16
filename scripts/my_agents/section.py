# balancesheet/agents/section_agent.py
"""
Generic helper: build an Agent that extracts ONE balance-sheet section.

Do NOT import this directly from orchestrator; use the concrete
make_assets_agent() / make_liabilities_agent() / make_equity_agent()
defined further below.
"""
from __future__ import annotations
from typing import Literal

from agents import Agent, ModelSettings
from models import SectionTable


_SECTION_PROMPT_TEMPLATE = """
You are a CPA-level financial statement analyst.

Task: Extract ONLY the {section_upper} section of the MOST RECENT
balance sheet presented in the provided SEC filing documents.

Return JSON that matches the SectionTable schema.  Requirements:
1. Preserve the filing's line-item order; do NOT rename items.
2. Multiply values whenever the statement says
      “$ in thousands”  (×1,000)  or  “$ in millions” (×1,000,000)
   so that *value is in whole USD*.
3. If the statement shows a subtotal line
      (“Total {section_lower}” etc.)
   add it to the `subtotal` field.
4. Copy any foot-note symbol or reference into `note_ref`.
5. Do not invent numbers or line items. If a number is missing, try again until you find it. 
6. If a line item is a total or a subtotal of other line items in this section, DO NOT INCLUDE IT
7. In the final output, do not include the Total of the entire section. 
"""

def make_section_agent(
        section: Literal['assets','liabilities','equity'],
        tool
) -> Agent:
    assert section in ('assets','liabilities','equity')
    prompt = _SECTION_PROMPT_TEMPLATE.format(
                section_upper = section.upper(),
                section_lower = section.lower()
            ) + (
                f'\n\nIMPORTANT: In the JSON you return, the "section" field '
                f'MUST be exactly "{section}".'
             )

    agent = Agent(
        name          = f"{section.capitalize()}Agent",
        model         = 'o3',   # or whatever default you want
        model_settings= ModelSettings(reasoning={'effort':'high'}),
        output_type   = SectionTable,
        instructions  = prompt,
        tools         = [tool]
    )
    # set default value in the schema so the LLM can't forget
    #agent.system_prompt += f'\n\nNOTE: The "section" field must equal "{section}".'
    return agent