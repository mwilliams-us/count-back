"""The count-back game engine: one round of building change up to the tender."""

from decimal import Decimal, ROUND_HALF_UP

from .generator import ProblemGenerator
from .models import DENOMINATIONS, Problem, StepOutcome, RoundResult

CENT = Decimal("0.01")

class CountBackGame:
    """State machine for a single round of count-back practice.

    Lifecycle: start_round() -> apply('penny') ... -> apply(denom) until
    running_total reaches paid. All feedback is returned as data,
    never printed. Works identically for CLI, Flask, or any future UI.
    """

    def __init__(self, level: int = 1):
        self.generator = ProblemGenerator(level)
        self.problem: Problem | None = None
        self.running_total: Decimal | None = None
        self.pieces_used: list[str] = []

    def start_round(self) -> Problem:
        """Deal a new customer. Resets all round state."""
        self.problem = self.generator.new_problem()
        self.running_total = self.problem.total
        self.pieces_used = []
        return self.problem

    @property
    def remaining(self) -> Decimal:
        """How much more change must be handed over."""
        return self.problem.paid - self.running_total

    def apply(self, denom_name: str) -> StepOutcome:
        """Hand over one piece of change. The single gameplay verb."""
        if self.problem is None:
            raise RuntimeError("start_round() before apply()")
        if denom_name not in DENOMINATIONS:
            return StepOutcome(False, self.running_total,
                               f"I don't know '{denom_name}'.")
        if denom_name not in self.problem.allowed_denoms:
            return StepOutcome(False, self.running_total,
                               f"A {denom_name} isn't available at this level.")

        piece = DENOMINATIONS[denom_name]
        new_total = self.running_total + piece.value

        if new_total > self.problem.paid:
            # No penalty: hand it back, try again (per Caesar's decree)
            over_by = new_total - self.problem.paid
            return StepOutcome(
                False, self.running_total,
                f"That's {self._money(over_by)} too much — "
                f"take the {denom_name} back."
            )

        self.running_total = new_total
        self.pieces_used.append(denom_name)

        if self.running_total == self.problem.paid:
            return StepOutcome(True, self.running_total,
                               "Perfect! Exact count-back.",
                               round_complete=True)
        return StepOutcome(True, self.running_total,
                           f"Now at {self._money(self.running_total)}.")

    def finish(self) -> RoundResult:
        """Player signals they're done. Grade the round."""
        if self.running_total == self.problem.paid:
            counts = {}
            for name in self.pieces_used:
                counts[name] = counts.get(name, 0) + 1
            summary = ", ".join(
                DENOMINATIONS[name].describe(n) for name, n in counts.items()
            )
            return RoundResult(won=True, pieces_used=list(self.pieces_used),
                               summary=summary)
        short = self.problem.paid - self.running_total
        return RoundResult(won=False,
                           summary=f"Still owe {self._money(short)}.")

    def hint(self) -> str:
        """Suggest the next piece using the friendly-numbers (greedy) route."""
        for name in sorted(self.problem.allowed_denoms,
                           key=lambda n: DENOMINATIONS[n].value,
                           reverse=True):
            if DENOMINATIONS[name].value <= self.remaining:
                return name
        return "penny"

    @staticmethod
    def _money(amount: Decimal) -> str:
        return f"${amount.quantize(CENT, ROUND_HALF_UP)}"