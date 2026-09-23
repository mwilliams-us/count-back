"""
Change Counting Practice — Count-Back Edition
Teaches the classic cashier skill: build from the total UP to the tender.
No penalties. Learning first.
"""

import random
from decimal import Decimal, ROUND_HALF_UP

CENT = Decimal("0.01")

# --- Domain -----------------------------------------------------------

DENOMINATIONS = {
    # name: value in dollars
    "penny":    Decimal("0.01"),
    "nickel":   Decimal("0.05"),
    "dime":     Decimal("0.10"),
    "quarter":  Decimal("0.25"),
    "dollar":   Decimal("1"),
    "five":     Decimal("5"),
    "ten":      Decimal("10"),
    "twenty":   Decimal("20"),
    "fifty":    Decimal("50"),
    "hundred":  Decimal("100"),
}

# --- Levels: which money she may receive, and typical totals ---------
LEVELS = [
    {"name": 1, "coins": ["penny", "nickel", "dime", "quarter", "dollar"],
     "max_total": Decimal("5")},
    {"name": 2, "coins": ["penny", "nickel", "dime", "quarter",
                           "dollar", "five"],
     "max_total": Decimal("20")},
    {"name": 3, "coins": ["penny", "nickel", "dime", "quarter",
                           "dollar", "five", "ten", "twenty"],
     "max_total": Decimal("50")},
    {"name": 4, "coins": list(DENOMINATIONS.keys()),
     "max_total": Decimal("100")},
]


def money(d):
    """Format a Decimal nicely."""
    return f"${d.quantize(CENT, ROUND_HALF_UP)}"


class Register:
    """One round of count-back practice."""

    def __init__(self, level):
        cfg = LEVELS[level - 1]
        self.allowed = cfg["coins"]
        # Random total, rounded to a realistic price (nickel at level 1
        # avoids brutal penny math early on)
        step = CENT if level > 1 else Decimal("0.05")
        raw = Decimal(str(random.uniform(0.25, float(cfg["max_total"]))))
        self.total = (raw // step) * step + step
        # Customer pays with the smallest bill that covers it (sometimes
        # the next one up for variety)
        bills = sorted(v for n, v in DENOMINATIONS.items()
                      if v >= self.total and "dollar" in str(n * 100).split(".")[0])
        tenders = [v for n, v in DENOMINATIONS.items()
                   if v in (Decimal("1"), Decimal("5"), Decimal("10"),
                            Decimal("20"), Decimal("50"), Decimal("100"))
                   and v >= self.total]
        self.paid = min(tenders) if tenders else Decimal("100")
        if len(tenders) > 1 and random.random() < 0.2:
            self.paid = tenders[1]
        self.running = self.total
        self.used = []

    def step(self, name):
        """Try handing over one piece. Returns (message, done)."""
        if name not in DENOMINATIONS:
            return "Hmm, I don't know that one.", False
        if name not in self.allowed:
            return f"Not unlocked yet — try: {', '.join(self.allowed)}", False
        new_total = self.running + DENOMINATIONS[name]
        if new_total > self.paid:
            # No penalty: hand it back
            return (f"Oops! {money(self.running)} + {name} is "
                    f"{money(new_total)} — that's past {money(self.paid)}."
                    f" Take it back and try something smaller."), False
        self.running = new_total
        self.used.append(name)
        if self.running == self.paid:
            return f"{money(self.running)} — PERFECT! You made it!", True
        return f"Now at {money(self.running)}...", False

    def hint(self):
        """Greedy count-back hint: the friendly-numbers route."""
        remaining = self.paid - self.running
        for name in reversed(sorted(self.allowed, key=lambda n: DENOMINATIONS[n])):
            if DENOMINATIONS[name] <= remaining and DENOMINATIONS[name] > 0:
                return name
        return "a tiny bit — pennies!"


# --- Game loop --------------------------------------------------------

def main():
    print("=" * 46)
    print("  COUNT-BACK CASH REGISTER PRACTICE")
    print("  Build the change UP to what they paid!")
    print("=" * 46)
    level = 1
    while True:
        lvl_pick = input(f"\nLevel 1-4 (Enter = {level}): ").strip()
        if lvl_pick in ("q", "quit"):
            break
        if lvl_pick.isdigit() and 1 <= int(lvl_pick) <= 4:
            level = int(lvl_pick)

        reg = Register(level)
        print(f"\n🧾 Total: {money(reg.total)}")
        print(f"💵 Customer paid with: {money(reg.paid)}")
        print(f"   Count back from {money(reg.total)} to {money(reg.paid)}!")

        while True:
            cmd = input("\nGive (penny/nickel/dime/quarter/... or 'hint' or 'q'): ").strip().lower()
            if cmd == "q":
                return
            if cmd == "hint":
                print(f"💡 Try a {reg.hint()}")
                continue
            msg, done = reg.step(cmd)
            print(msg)
            if done:
                print(f"You used {len(reg.used)} pieces: {', '.join(reg.used)}")
                print("Great counting! 🎉")
                break

        again = input("\nAnother customer? (y/n): ").strip().lower()
        if again != "y":
            break
    print("Thanks for practicing! 💰")


if __name__ == "__main__":
    main()