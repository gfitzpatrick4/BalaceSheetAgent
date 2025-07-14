from __future__ import annotations

#TODO: single source of truth for the schemas that all agents import 


# balancesheet/models.py
"""
Pydantic data objects used by *all* agents.

Never put business logic here – only data structures and the
smallest possible helper methods (e.g. totals).
"""


from typing import List, Literal, Optional

from pydantic import BaseModel, Field, computed_field


class BalanceSheetLine(BaseModel):
    line_item:  str
    value:      float                # always in whole USD, never “in thousands”
    unit:       Literal['USD', 'shares'] = 'USD'
    as_of_date: Optional[str] = None  # yyyy-mm-dd if available
    note_ref:   Optional[str] = None  # e.g. '(1)', 'See Note 4'
    components: list["BalanceSheetLine"] | None = None   # NEW

    model_config = {"extra": "forbid"}

    @property
    def total_value(self) -> float:
        """recursively sum this line and any sub-components."""
        subtotal = self.value or 0.0
        if self.components:
            subtotal += sum(c.total_value for c in self.components)
        return subtotal


class SectionTable(BaseModel):
    """
    One of: assets, liabilities, equity
    """
    section:   Literal['assets', 'liabilities', 'equity']
    lines:     List[BalanceSheetLine]
    subtotal:  Optional[float] = None

    @computed_field
    @property
    def total(self) -> float:
        """
        Convenience: sum of individual line values if subtotal is missing.
        """
        return sum(l.total_value for l in self.lines)


class FullBalanceSheet(BaseModel):
    company_name: str
    cik:          str
    filing_date:  str               # date the 10-Q/10-K was filed
    period_end:   Optional[str]     # ‘As of’ date from the statement
    tables:       List[SectionTable]
    shares_outstanding_common: Optional[int] = None
    shares_outstanding_preferred: Optional[int] = None
    update_errors: list["FailedChange"] | None = None
    applied_updates: list["FilingChange"] | None = None

    # helper getters
    @property
    def assets(self) -> SectionTable:
        return next(t for t in self.tables if t.section == 'assets')

    @property
    def liabilities(self) -> SectionTable:
        return next(t for t in self.tables if t.section == 'liabilities')

    @property
    def equity(self) -> SectionTable:
        return next(t for t in self.tables if t.section == 'equity')
    def balance_difference(self) -> float:
        """return assets minus (liabilites + equity) using computed totals"""
        return self.assets.total - (self.liabilities.total + self.equity.total)

    @property
    def balanced(self) -> bool:
        return abs(self.balance_difference()) < 0.01
    
BalanceSheetLine.model_rebuild()

class BalanceSheetDelta(BaseModel):
    section: Literal['assets','liabilities','equity']
    line_item: str
    delta: float

class FilingChange(BaseModel):
    date: str
    deltas: List[BalanceSheetDelta]
    citation: str

class FailedChange(BaseModel):
    """Represents an update that could not be applied without causing an imbalance."""
    change: FilingChange
    attempted_fix: FilingChange | None = None
    reason: str

class UpdateSummary(BaseModel):
    changes: List[FilingChange]
    total_common_shares: Optional[int] = None
    total_preferred_shares: Optional[int] = None

FullBalanceSheet.model_rebuild()