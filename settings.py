# balancesheet/settings.py
"""
Loads the corporate OpenAI key and exposes a shared OpenAI_CLIENT.
Runs once when the balancesheet package is imported.
"""

import json, os, openai
from agents import set_default_openai_key, set_tracing_export_api_key   # already in your env

# --- COPY–PASTED SNIPPET ---------------------------------------------------
provider = "openai"
user     = "CACS"

with open("//fs1/shares/dept/trading/specialsituations/Working/MARIO/AI/data/keys.json", "r") as f:
    creds   = json.load(f)[provider]
    env_var = creds["env_var"]          # e.g. "OPENAI_API_KEY"
    key     = creds["keys"][user]

os.environ[env_var] = key               # makes it visible to any downstream lib
set_default_openai_key(key)
set_tracing_export_api_key(key)
# ---------------------------------------------------------------------------

OpenAI_CLIENT = openai.OpenAI(api_key=key)


def get_openai_client() -> openai.OpenAI:
    """Single shared client for the whole program."""
    return OpenAI_CLIENT