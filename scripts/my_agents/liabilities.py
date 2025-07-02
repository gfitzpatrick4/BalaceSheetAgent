# balancesheet/agents/liabilities_agent.py
from .section import make_section_agent

def make_liabilities_agent(tool):
    return make_section_agent('liabilities', tool)