"""Generates practice transactions: a random total plus a plausible payment."""

import random
from decimal import Decimal

from .models import Denomination, DENOMINATIONS

CENT = Decimal("0.01")

# Bill values a customer might hand over, ascending
BILL_VALUES = [
    Decimal("1"), Decimal("5"), Decimal("10"),
    Decimal("20"), Decimal("50"), Decimal("100"),
]

class LevelConfig:
    """Difficulty settings for one level."""

    def __init__(self, name, allowed_denoms, max_total, stretch=False):
        self.name = name
        self.allowed_denoms = allowed_denoms
        self.max_total = max_total
        self.stretch = stretch

LEVELS: list[LevelConfig] = [
    # Level 1: coins + singles, small totals, gentle payments
    LevelConfig(1, ["penny", "nickel", "dime", "quarter", "dollar"],
                Decimal("5")),
    # Level 2: fives join, bigger totals
    LevelConfig(2, ["penny", "nickel", "dime", "quarter",
                     "dollar", "five"],
                Decimal("20")),
    # Level 3: tens and twenties; occasional big-bill customers
    LevelConfig(3, ["penny", "nickel", "dime", "quarter", "dollar",
                     "five", "ten", "twenty"],
                Decimal("50"), stretch=True),
    # Level 4: full vault access
    LevelConfig(4, list(DENOMINATIONS.keys()),
                Decimal("100"), stretch=True),
]

class ProblemGenerator:
    """Creates Problem instances for a given difficulty level."""

    def __init__(self, level: int = 1):
        self.level = level

    @property
    def config(self) -> LevelConfig:
        return LEVELS[self.level - 1]

    def _random_total(self) -> Decimal:
        """A realistic price, rounded to the nickel at level 1."""
        step = Decimal("0.05") if self.level == 1 else CENT
        raw = Decimal(str(random.uniform(0.25, float(self.config.max_total))))
        # Round DOWN to a multiple of step, then add one step so we
        # never land exactly on the max
        return ((raw // step) * step + step).quantize(CENT)

    def _plausible_payment(self, total: Decimal) -> Decimal:
        """Smallest bill that covers the total; occasionally one larger
        ('stretch' customers) at high levels only."""
        tenders = [v for v in BILL_VALUES if v >= total]
        paid = tenders[0]
        if (self.config.stretch and len(tenders) > 1
                and random.random() < 0.2):
            paid = tenders[1]
        return paid

    def new_problem(self):
        """Build a fresh Problem. Returns Problem from models."""
        from .models import Problem  # local import avoids cycles
        total = self._random_total()
        paid = self._plausible_payment(total)
        return Problem(
            total=total,
            paid=paid,
            level=self.level,
            allowed_denoms=self.config.allowed_denoms,
        )