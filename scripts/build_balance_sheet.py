"""
Command-line entry-point.

Usage examples
--------------
# one company
python scripts/build_balance_sheet.py 1805526 https://www.sec.gov/Archives/edgar/data/1805526/000121390025042977/0001213900-25-042977-index.html

build_balance_sheet.py 1849635 https://www.sec.gov/Archives/edgar/data/1849635/000114036125018209/0001140361-25-018209-index.html

build_balance_sheet.py 1360442 https://www.sec.gov/Archives/edgar/data/1360442/000109690625000870/0001096906-25-000870-index.html
build_balance_sheet.py 1922858 https://www.sec.gov/Archives/edgar/data/1922858/000121390025046180/0001213900-25-046180-index.html
build_balance_sheet.py 1889123 https://www.sec.gov/Archives/edgar/data/1889123/000095017025072818/0000950170-25-072818-index.html
build_balance_sheet.py 1687542 https://www.sec.gov/Archives/edgar/data/1687542/000164117225011165/0001641172-25-011165-index.html
build_balance_sheet.py 1641398 https://www.sec.gov/Archives/edgar/data/1641398/000121390025044218/0001213900-25-044218-index.html
build_balance_sheet.py 1830072 https://www.sec.gov/Archives/edgar/data/1830072/000168316825003710/0001683168-25-003710-index.html
build_balance_sheet.py 2022308 https://www.sec.gov/Archives/edgar/data/2022308/000192998025000446/0001929980-25-000446-index.html
build_balance_sheet.py 1074828 https://www.sec.gov/Archives/edgar/data/1074828/000165495425005607/0001654954-25-005607-index.html
build_balance_sheet.py 1662684 https://www.sec.gov/Archives/edgar/data/1662684/000141057825001326/0001410578-25-001326-index.html
build_balance_sheet.py 1050446 https://www.sec.gov/Archives/edgar/data/1050446/000095017025063536/0000950170-25-063536-index.html
build_balance_sheet.py 1946573 https://www.sec.gov/Archives/edgar/data/1946573/000164117225009328/0001641172-25-009328-index.html
build_balance_sheet.py 1836875 https://www.sec.gov/Archives/edgar/data/1836875/000183687525000102/0001836875-25-000102-index.html
build_balance_sheet.py 1784970 https://www.sec.gov/Archives/edgar/data/1784970/000121390025041307/0001213900-25-041307-index.html
build_balance_sheet.py 1849380 https://www.sec.gov/Archives/edgar/data/1849380/000164117225010321/0001641172-25-010321-index.html
build_balance_sheet.py 1981535 https://www.sec.gov/Archives/edgar/data/1981535/000164117225010881/0001641172-25-010881-index.html
build_balance_sheet.py 2015947 https://www.sec.gov/Archives/edgar/data/2015947/000141057825001232/0001410578-25-001232-index.html
build_balance_sheet.py 1554859 https://www.sec.gov/Archives/edgar/data/1554859/000155485925000020/0001554859-25-000020-index.html
build_balance_sheet.py 1571934 https://www.sec.gov/Archives/edgar/data/1571934/000141057825001327/0001410578-25-001327-index.html
build_balance_sheet.py 1853825 https://www.sec.gov/Archives/edgar/data/1853825/000164117225011020/0001641172-25-011020-index.html
build_balance_sheet.py 1775194 https://www.sec.gov/Archives/edgar/data/1775194/000147793225003866/0001477932-25-003866-index.html
build_balance_sheet.py 1671941 https://www.sec.gov/Archives/edgar/data/1671941/000155837025007836/0001558370-25-007836-index.html
build_balance_sheet.py 1816937 https://www.sec.gov/Archives/edgar/data/1816937/000164117225011696/0001641172-25-011696-index.html


# if you save the URL in a JSON dict you could read it here instead
"""
"""import sys, asyncio, argparse
from EdgarCache.Client.Client import Client as EC

from orchestrator import build_balance_sheet
from pretty import pretty_print



def parse_args():
    p = argparse.ArgumentParser(prog="build_balance_sheet")
    p.add_argument("cik", type=int, help="CIK of the company")
    p.add_argument("index_url", help="10-Q/10-K index.html URL on sec.gov")
    return p.parse_args()


async def main():
    args  = parse_args()

    # Connect to your in-house EDGAR cache
    ec = EC('ny4-35.bluefintrading.com', 8361)

    # run the full multi-agent pipeline
    bs = await build_balance_sheet(args.cik, args.index_url, ec)

    # pretty print to console
    pretty_print(bs)


if __name__ == "__main__":
    asyncio.run(main())"""


"""
build_balance_sheet.py

This file can now be:
1. Imported and called as a function:
       from build_balance_sheet import get_balance_sheet
       bs = get_balance_sheet(1849635, some_url)

2. Run from the shell exactly like before:
       python build_balance_sheet.py 1849635 <url>

---------------------------------------------------------------------
"""

import asyncio
import argparse
from typing import Any

from EdgarCache.Client.Client import Client as EC
from orchestrator import build_balance_sheet as _orchestrator_build_balance_sheet
import pprint as pprint
from pretty import pretty_print

###############################################################################
# 1. Low-level async “library” function
###############################################################################
async def build_balance_sheet_async(
    cik: int,
    index_url: str,
    ec_host: str = "ny4-35.bluefintrading.com",
    ec_port: int = 8361,
) -> Any:
    """
    The core coroutine that does the actual work.

    Parameters
    ----------
    cik : int
        The company CIK.
    index_url : str
        SEC index.html URL (10-K / 10-Q filing).
    ec_host, ec_port : str | int
        Where your in-house EDGAR-cache service lives.

    Returns
    -------
    Any   # whatever `orchestrator.build_balance_sheet` returns
    """
    print("Running async")
    ec = EC(ec_host, ec_port)          # you can also `async with EC(...)`
    return await _orchestrator_build_balance_sheet(cik, index_url, ec)


###############################################################################
# 2. Optional sync wrapper so callers don’t need to touch asyncio
###############################################################################
def get_balance_sheet(
    cik: int,
    index_url: str,
    ec_host: str = "ny4-35.bluefintrading.com",
    ec_port: int = 8361,
    pretty: bool = False,
):
    """
    Synchronous helper around `build_balance_sheet_async`.

    Example
    -------
    >>> from build_balance_sheet import get_balance_sheet
    >>> bs = get_balance_sheet(1849635, some_url, pretty=True)
    """
    result = asyncio.run(
        build_balance_sheet_async(cik, index_url)
    )
    if pretty:
        pretty_print(result)
    return result


###############################################################################
# 3. CLI wrapper (argparse) – unchanged behaviour
###############################################################################
def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(prog="build_balance_sheet")
    p.add_argument("cik", type=int, help="CIK of the company")
    p.add_argument("index_url", help="10-Q / 10-K index.html URL on sec.gov")
    return p.parse_args()


async def _main_cli():
    args = _parse_args()
    initial_bs, updated_bs = await build_balance_sheet_async(args.cik, args.index_url)
    pretty_print(initial_bs, updated_bs)


if __name__ == "__main__":
    asyncio.run(_main_cli())