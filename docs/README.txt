Multi-agent Python workflow that downloads a company’s most-recent SEC filing,  
re-assembles a **fully-detailed balance sheet**, and prints it in a readable
table—no manual copy/paste from 10-Q’s ever again.

-------------------------------------------------------------------------------
Why does it exist?
-------------------------------------------------------------------------------
Finance teams waste hours transcribing the same three pages of every filing.
LLMs can read HTML, but they often hallucinate numbers.  
This repo solves both problems:

1.  Pull 10-Q / 10-K documents from Bluefin’s internal EDGAR cache.  
2.  Hand the raw **balance-sheet table** to a specialised agent so it must
    copy values verbatim.  
3.  Spin up three child agents—`assets`, `liabilities`, `equity`—that return
    structured JSON for their section only.  
4.  Run a fourth `expander` agent that finds any “Other, net” roll-ups and
    replaces them with their note-level breakdown.  
5.  Feed everything to an `assembler` agent that verifies  
    Assets = Liabilities + Equity and outputs a canonical JSON object.  
6.  Pretty-print the result as a GitHub-style table in the console.

-------------------------------------------------------------------------------
Core workflow
-------------------------------------------------------------------------------
1. **Download** index.html via `EdgarCacheClient`.
2. **Extract** the `<table>` that contains “Total assets” & “Total liabilities”.
3. **Section agents** copy rows for their subsection only.
4. **Expander agent** pulls note tables for “Other / Net” roll-ups.
5. **Assembler agent** merges sections, checks the accounting equation.
6. **pretty_print()** renders the final `FullBalanceSheet`.

-------------------------------------------------------------------------------
Dependencies
-------------------------------------------------------------------------------
• openai >= 1.14 (Assistants + Vector Store)  
• agents (https://github.com/gkamradt/agents)  
• beautifulsoup4, lxml, pydantic, tqdm, tabulate  
• Bluefin internal  `EdgarCache.Client`

-------------------------------------------------------------------------------
Configuration
-------------------------------------------------------------------------------
`balancesheet/settings.py` reads  
`//fs1/.../AI/data/keys.json`, picks provider `openai`, user `CACS`, and sets
`OPENAI_API_KEY` automatically.  No manual secret handling required.

-------------------------------------------------------------------------------
Road-map
-------------------------------------------------------------------------------
☐  Income-statement & cash-flow agents  
☐  Streamlit front-end with search by ticker  
☐  SQLite cache of finished balance-sheets for back-tests  
☐  Unit-test suite in `tests/` + CI badge

-------------------------------------------------------------------------------
License / Disclaimer
-------------------------------------------------------------------------------
Internal Bluefin tool.  Not for external distribution.  
Financial figures are transcribed; always validate against the source filing
before trading decisions.
