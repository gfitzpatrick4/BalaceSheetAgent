from __future__ import annotations
from typing import Iterable
from models import FullBalanceSheet, BalanceSheetLine
from tabulate import tabulate         # pip install tabulate


def _flatten(lines: Iterable[BalanceSheetLine], indent: int = 0):
    """
    Converts hierarchical BalanceSheetLine objects into rows
    (indent controls left-padding for components).
    """
    for ln in lines:
        yield [" " * indent + ln.line_item, f"{ln.value:,.0f}"]
        if ln.components:
            yield from _flatten(ln.components, indent + 2)


def pretty_print(bs: FullBalanceSheet):
    print(f"\n{bs.company_name}   CIK {bs.cik}")
    print(f"Filing date: {bs.filing_date}   Period end: {bs.period_end}\n")

    for section in bs.tables:               # assets, liabilities, equity
        print(section.section.upper())
        rows = list(_flatten(section.lines))
        if section.subtotal:
            rows.append(["TOTAL " + section.section.upper(),
                         f"{section.subtotal:,.0f}"])
        print(tabulate(rows, headers=["Line Item", "USD"], tablefmt="github"))
        print()                             # blank line between sections

    # Optional balance check
    if bs.balanced:
        print("✓ Balanced (Assets = Liab + Equity)\n")
    else:
        print("⚠ NOT balanced! Check totals.\n")