from __future__ import annotations
from typing import Iterable
from itertools import zip_longest
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


def pretty_print(original: FullBalanceSheet, updated: FullBalanceSheet | None = None):
    """Print one or two balance sheets in a readable table."""

    if updated is None:
        print(f"\n{original.company_name}   CIK {original.cik}")
        print(f"Filing date: {original.filing_date}   Period end: {original.period_end}\n")

        for section in original.tables:
            print(section.section.upper())
            rows = list(_flatten(section.lines))
            if section.subtotal:
                rows.append(["TOTAL " + section.section.upper(), f"{section.subtotal:,.0f}"])
            print(tabulate(rows, headers=["Line Item", "USD"], tablefmt="github"))
            print()

        if original.balanced:
            print("✓ Balanced (Assets = Liab + Equity)\n")
        else:
            print("⚠ NOT balanced! Check totals.\n")
        return

    print(f"\n{original.company_name}   CIK {original.cik}")
    print(
        f"Filing date: {original.filing_date}   Period end: {original.period_end}\n"
    )

    for section in original.tables:
        print(section.section.upper())
        updated_section = next(t for t in updated.tables if t.section == section.section)

        orig_rows = list(_flatten(section.lines))
        if section.subtotal:
            orig_rows.append(["TOTAL " + section.section.upper(), f"{section.subtotal:,.0f}"])

        upd_rows = list(_flatten(updated_section.lines))
        if updated_section.subtotal:
            upd_rows.append(["TOTAL " + updated_section.section.upper(), f"{updated_section.subtotal:,.0f}"])

        rows = []
        for o, u in zip_longest(orig_rows, upd_rows, fillvalue=["", ""]):
            label = o[0] if o[0] else u[0]
            rows.append([label, o[1], u[1]])

        headers = ["Line Item", original.filing_date, "Updated"]
        print(tabulate(rows, headers=headers, tablefmt="github"))
        print()

    if updated.balanced:
        print("✓ Balanced (Assets = Liab + Equity)\n")
    else:
        print("⚠ NOT balanced! Check totals.\n")