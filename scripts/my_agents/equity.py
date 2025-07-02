# balancesheet/agents/equity_agent.py
from .section import make_section_agent

def make_equity_agent(tool):
    return make_section_agent('equity', tool)