"""The count-back game engine: one round of building change up to the tender."""

from decimal import Decimal, ROUND_HALF_UP

from .generator import ProblemGenerator
from .models import DENOMINATIONS, Problem, StepOutcome, RoundResult

CENT = Decimal("0.01")
QUARTER = Decimal("0.25")

class CountBackGame:
    """State machine for a single round of count-back practice.

    Lifecycle: start_round() -> apply('penny') ... -> apply(denom) until
    running_total reaches paid. All feedback is returned as data,
    never printed. Works identically for CLI, Flask, or any future UI.

    Modes:
      - "simulation": free play — any non-overshooting piece is accepted.
      - "learning":   strict — pieces MUST follow the canonical
                      count-back route (next_piece()), which builds
                      change with the fewest pieces per denomination step.
    """

    def __init__(self, level: int = 1, mode: str = "simulation"):
        self.generator = ProblemGenerator(level)
        self.mode = mode               # "simulation" | "learning"
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

    @property
    def is_learning(self) -> bool:
        return self.mode == "learning"

    def apply(self, denom_name: str) -> StepOutcome:
        """Hand over one piece of change. The single gameplay verb."""
        if self.problem is None:
            raise RuntimeError("call start_round() before apply()")
        if denom_name not in DENOMINATIONS:
            return StepOutcome(False, self.running_total,
                               f"I don't know '{denom_name}'.")
        if denom_name not in self.problem.allowed_denoms:
            return StepOutcome(False, self.running_total,
                               f"A {denom_name} isn't available at this level.")

        # Learning Mode: enforce the canonical count-back route.
        # The piece flies back to the drawer; state is untouched.
        if self.is_learning and denom_name != self.next_piece():
            expected = self.next_piece()
            return StepOutcome(
                False, self.running_total,
                f"Wait! The cashier way is {expected} next — "
                f"try a {expected}."
            )

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

    def next_piece(self) -> str:
        """The canonical count-back next piece (the family algorithm).

        Work from the TOTAL we are counting up, not the remaining:
        pennies to a 0/5 ending; then climb to the next quarter mark
        (d = distance: 5=nickel, 10=dime, 15=nickel+dime, 20=dime+dime);
        quarters to the dollar; then ones climb to a multiple of the
        smallest big bill and larger bills close.

        Safe by construction: the customer pays a whole-dollar bill, so
        the next quarter mark never exceeds paid — the suggested piece
        always fits in the remaining change.
        """
        remaining = self.remaining
        total_cents = int(self.running_total * 100)
        rem_cents = int(remaining * 100) % 100

        if total_cents % 5 != 0:               # pennies to a 0/5 ending
            return "penny"

        d = (25 - total_cents % 25) % 25       # distance to quarter mark
        if d == 5:
            return "nickel"
        if d == 10:
            return "dime"
        if d == 15:
            return "nickel"                    # then a dime — the family way
        if d == 20:
            return "dime"

        # At (or past consideration of) a quarter mark:
        if rem_cents != 0:                     # quarters to the dollar
            return "quarter"

        # BILLS: ones climb until remaining is a multiple of the
        # smallest unlocked big bill; then the largest bill that fits.
        allowed_bills = [n for n in self.problem.allowed_denoms
                         if DENOMINATIONS[n].value >= Decimal("5")]
        climb_target = Decimal("5") if allowed_bills else Decimal("1")
        whole = remaining.to_integral_value()
        if allowed_bills and (whole % climb_target) != 0:
            return "dollar"
        if not allowed_bills:
            return "dollar"
        for name in sorted(allowed_bills,
                           key=lambda n: DENOMINATIONS[n].value,
                           reverse=True):
            if DENOMINATIONS[name].value <= remaining:
                return name
        return "dollar"

    def hint(self) -> str:
        """Suggest the next piece — delegates to the count-back route
        so hints, grading, and Learning-mode enforcement all agree."""
        return self.next_piece()

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

    @staticmethod
    def _money(amount: Decimal) -> str:
        return f"${amount.quantize(CENT, ROUND_HALF_UP)}"