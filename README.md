# 💰 Count-Back Cash Register

A web-based training app for the classic cashier skill: making change by
**counting back** — building from the purchase total up to the amount the
customer handed you, the way a veteran register-jockey does it.

**▶ Play it live: https://count-back.onrender.com/**

Built with Flask, Jinja2, and vanilla JS. No build step, no dependencies
beyond Flask itself.

## 🎯 What It Teaches

Real-world count-back technique, enforced step by step:

> Total $2.33, customer pays $5 → two pennies to $2.35 → nickel to $2.40 →
> dime to $2.50 → two quarters to $3.00 → two dollars to $5.00.

The canonical route always uses the fewest pieces per denomination stage
(never five dimes where two quarters will do).

## 🕹️ Two Modes

- **🎓 Learning** — strict enforcement. You must follow the canonical
  count-back route; wrong picks bounce back. No penalty, just discipline.
- **🎲 Simulation** — free play. Make change any valid way you like.

## ✨ Features

- Realistic top-down cash drawer: 4 bill slots over 4 coin trays
- **Lift the insert (⤒)** to reveal the $50/$100 stash underneath the tray
  block, just like a real register
- Change pile with running total and per-piece display
- 💡 Hint toggle (persistent per mode) — defaults ON for Learning, OFF for
  Simulation; teaching feedback is silenced when OFF
- 4 difficulty levels gating which denominations are unlocked
- Level and mode switching instantly respawns the transaction
- Single-page feel: all interactions via JSON API, no page reloads

## 🚀 Running Locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install flask
python app.py