"""Domain objects for the count-back cash register game."""

from dataclasses import dataclass, field
from decimal import Decimal


@dataclass(frozen=True)
class Denomination:
    name: str
    value: Decimal
    plural: str

    def describe(self, count: int) -> str:
        return f"{count} {self.plural if count > 1 else self.name}"


DENOMINATIONS: dict[str, Denomination] = {
    d.name: d for d in [
        Denomination("penny",   Decimal("0.01"), "pennies"),
        Denomination("nickel",  Decimal("0.05"), "nickels"),
        Denomination("dime",    Decimal("0.10"), "dimes"),
        Denomination("quarter", Decimal("0.25"), "quarters"),
        Denomination("dollar",  Decimal("1"),    "dollars"),
        Denomination("five",   Decimal("5"),    "fives"),
        Denomination("ten",    Decimal("10"),   "tens"),
        Denomination("twenty", Decimal("20"),   "twenties"),
        Denomination("fifty",  Decimal("50"),   "fifties"),
        Denomination("hundred", Decimal("100"), "hundreds"),
    ]
}


@dataclass
class Problem:
    """One customer transaction: total and amount tendered."""
    total: Decimal
    paid: Decimal
    level: int
    allowed_denoms: list[str] = field(default_factory=list)

    @property
    def change_due(self) -> Decimal:
        return self.paid - self.total


@dataclass
class StepOutcome:
    """Result of handing over one piece of change."""
    success: bool
    running_total: Decimal
    message: str
    round_complete: bool = False


@dataclass
class RoundResult:
    """Final verdict when a round ends."""
    won: bool
    pieces_used: list[str] = field(default_factory=list)
    summary: str = ""