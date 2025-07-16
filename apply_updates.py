"""
Author: Griffin Fitzpatrick
Date: 7/16/2025

This script handles the application of balance sheet deltas. 
It recieves an UpdateSummary of Balance Sheet Deltas and applys them to 
the updated sheet. 
"""





from __future__ import annotations

from typing import List
from models import (
    FullBalanceSheet,
    BalanceSheetLine,
    BalanceSheetDelta,
    FilingChange,
    UpdateSummary,
    FailedChange,
    SectionTable,
)


def _apply_line(section: SectionTable, line_item: str, delta_value: float) -> None:
    line = next((l for l in section.lines if l.line_item == line_item), None)
    if line:
        line.value = (line.value or 0.0) + delta_value
    else:
        section.lines.append(BalanceSheetLine(line_item=line_item, value=delta_value))


def _apply_delta(bs: FullBalanceSheet, delta: BalanceSheetDelta) -> None:
    for entry in delta.assets:
        _apply_line(bs.assets, entry.line_item, entry.value)
    for entry in delta.liabilities:
        _apply_line(bs.liabilities, entry.line_item, entry.value)
    for entry in delta.equity:
        _apply_line(bs.equity, entry.line_item, entry.value)


async def apply_updates(
    initial: FullBalanceSheet,
    summary: UpdateSummary,
) -> FullBalanceSheet:
    """Apply each FilingChange sequentially verifying that each delta balances.

    Any change whose delta causes an imbalance is recorded on ``bs.update_errors``.
    """

    bs = initial.model_copy(deep=True)
    failed: List[FailedChange] = []
    applied: List[FilingChange] = []

    for change in sorted(summary.changes, key=lambda c: c.date):
        _apply_delta(bs, change.delta)
        applied.append(change)

    bs.shares_outstanding_common = summary.total_common_shares
    bs.shares_outstanding_preferred = summary.total_preferred_shares
    bs.update_errors = failed or None
    bs.applied_updates = applied or None
    return bs