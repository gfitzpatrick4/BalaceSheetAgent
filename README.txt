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
Directory layout
-------------------------------------------------------------------------------
balancesheet-bot/
│
├─ balancesheet/                ←  importable Python package
│  ├─ models.py                 Pydantic schemas (recursive BalanceSheetLine)
│  ├─ tools.py                  EDGAR, VectorStore, HTML helpers
│  ├─ settings.py               Loads OpenAI key from shared `keys.json`
│  ├─ pretty.py                 Console / Markdown renderers
│  ├─ agents/                   Agent factories
│  │   ├─ assets_agent.py
│  │   ├─ liabilities_agent.py
│  │   ├─ equity_agent.py
│  │   ├─ expander_agent.py
│  │   └─ assembler_agent.py
│  └─ orchestrator.py           Glues everything together
│
├─ scripts/
│  ├─ build_balance_sheet.py    ←  CLI you actually run
│  └─ batch_run.py              Batch over many CIKs (optional)
│
└─ README.md                    You are here

-------------------------------------------------------------------------------
Quick-start
-------------------------------------------------------------------------------
1.  Activate the Bluefin Conda env (Python ≥3.10).

2.  Install deps (once):
    ```
    pip install -r requirements.txt
    ```

3.  Make sure the shared key file exists:
    ```
    //fs1/.../AI/data/keys.json
    ```

4.  Run a single company:
    ```
    python scripts/build_balance_sheet.py \
        1805526 \
        https://www.sec.gov/Archives/edgar/data/1805526/000121390025042977/0001213900-25-042977-index.html
    ```

    Console output:
    ```
    ACME CORP           CIK 1805526
    Filing date: 2024-05-10   Period end: 2024-03-31

    ASSETS
    | Line Item                         |        USD |
    |----------------------------------|------------|
    | Cash and cash equivalents         |  1,801,575 |
    | Accounts receivable               |    631,441 |
    | …                                …|          … |
    | Other assets                      |     21,145 |
    |   Security deposits               |      9,000 |
    |   Long-term prepaids              |     12,145 |
    | TOTAL ASSETS                      |  4,158,049 |

    (Liabilities & Equity …)
    ✓ Balanced (Assets = Liab + Equity)
    ```

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