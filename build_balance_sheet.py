"""
Command-line entry-point.

Usage examples
--------------
# one company
python scripts/build_balance_sheet.py 1805526 https://www.sec.gov/Archives/edgar/data/1805526/000121390025042977/0001213900-25-042977-index.html

# if you save the URL in a JSON dict you could read it here instead
"""
import sys, asyncio, argparse
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
    asyncio.run(main())