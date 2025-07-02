# balancesheet/agents/assets_agent.py
from .section import make_section_agent

def make_assets_agent(tool):
    return make_section_agent('assets', tool)