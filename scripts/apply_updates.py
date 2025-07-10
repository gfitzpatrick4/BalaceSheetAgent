from __future__ import annotations

import json
from typing import List

from agents import Agent, Runner
from models import (
    FullBalanceSheet,
    BalanceSheetLine,
    BalanceSheetDelta,
    FilingChange,
    UpdateSummary,
    FailedChange,
)


def _apply_delta(bs: FullBalanceSheet, delta: BalanceSheetDelta) -> None:
    section = getattr(bs, delta.section)
    line = next((l for l in section.lines if l.line_item == delta.line_item), None)
    if line:
        line.value = (line.value or 0.0) + delta.delta
    else:
        section.lines.append(BalanceSheetLine(line_item=delta.line_item, value=delta.delta))


async def apply_updates(
    initial: FullBalanceSheet,
    summary: UpdateSummary,
    fixer: Agent | None = None,
) -> FullBalanceSheet:
    """Apply each FilingChange sequentially, verifying balance after every step.

    If a change introduces an imbalance it is sent to ``fixer`` for correction.
    Unresolved changes are recorded on ``bs.update_errors``.
    """

    bs = initial.model_copy(deep=True)
    failed: List[FailedChange] = []
    applied: List[FilingChange] = []

    for change in sorted(summary.changes, key=lambda c: c.date):
        snapshot = bs.model_copy(deep=True)

        for delta in change.deltas:
            _apply_delta(bs, delta)

        if bs.balanced:
            applied.append(change)
            continue

        if fixer is not None:
            resp = await Runner.run(
                fixer,
                json.dumps({
                    "balance_sheet": snapshot.model_dump(),
                    "change": change.model_dump(),
                    "error": "Update caused imbalance. Provide corrected FilingChange",
                }),
            )
            corrected: FilingChange = resp.final_output

            bs_corrected = snapshot.model_copy(deep=True)
            for delta in corrected.deltas:
                _apply_delta(bs_corrected, delta)

            if bs_corrected.balanced:
                bs = bs_corrected
                applied.append(corrected)
                continue

            failed.append(
                FailedChange(
                    change=change,
                    attempted_fix=corrected,
                    reason=f"still unbalanced by {bs_corrected.balance_difference():.2f}"
                )
            )
            bs = snapshot  # revert to last balanced state
        else:
            failed.append(FailedChange(change=change, reason="unbalanced"))
            bs = snapshot

    bs.shares_outstanding_common = summary.total_common_shares
    bs.shares_outstanding_preferred = summary.total_preferred_shares
    bs.update_errors = failed or None
    bs.applied_updates = applied or None
    return bs
