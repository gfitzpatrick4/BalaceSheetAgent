from agents import Agent, ModelSettings
from models import SectionTable

_PROMPT = """
You will receive ONE SectionTable JSON object plus full access to the filing
through the FileSearchTool.

For every line where that represents a sum of something that nots a total, such as 'other assets'
do the following:
  1. Search the filing for the accompanying notes that detail the components of that line item.
  2. Extract the component line items and their values.
  3. Replace the parent line by the same parent *plus* a `components` array
     that lists each component.  Parent `value` must equal the sum.

Return a VALID SectionTable JSON; do not change the subtotal.
"""

def make_expander_agent(tool):
    return Agent(
        name="NoteExpander",
        model="o3",
        model_settings=ModelSettings(),
        output_type=SectionTable,
        instructions=_PROMPT,
        tools=[tool],
    )