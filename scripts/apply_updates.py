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
        for item, val in entry.items():
            _apply_line(bs.assets, item, val)
    for entry in delta.liabilities:
        for item, val in entry.items():
            _apply_line(bs.liabilities, item, val)
    for entry in delta.equity:
        for item, val in entry.items():
            _apply_line(bs.equity, item, val)


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
        if change.delta is None:
            failed.append(FailedChange(change=change, reason="missing delta"))
            continue

        if not change.delta.balanced:
            failed.append(FailedChange(change=change, reason="delta not balanced"))
            continue

        snapshot = bs.model_copy(deep=True)
        _apply_delta(bs, change.delta)

        if bs.balanced:
            applied.append(change)
        else:
            diff = bs.balance_difference()
            bs = snapshot
            failed.append(
                FailedChange(change=change, reason=f"unbalanced by {diff:.2f} after apply")
            )

    bs.shares_outstanding_common = summary.total_common_shares
    bs.shares_outstanding_preferred = summary.total_preferred_shares
    bs.update_errors = failed or None
    bs.applied_updates = applied or None
    return bs