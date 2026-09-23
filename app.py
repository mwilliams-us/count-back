"""Flask adapter: exposes the count-back game as a clickable web app."""

from flask import Flask, render_template, request, redirect, url_for, flash

from cashback.game import CountBackGame
from cashback.models import DENOMINATIONS

app = Flask(__name__)
app.secret_key = "countback-dev"   # needed for flash messages; change in production

# ONE game object per process (fine for a single player on one machine)
game = CountBackGame(1)

@app.route("/")
def index():
    if game.problem is None:
        game.start_round()
    summary = ""
    change_returned = ""
    if game.running_total == game.problem.paid:
        result = game.finish()
        summary = result.summary
        change_returned = (game.running_total - game.problem.total)
    return render_template("index.html", game=game, denoms=DENOMINATIONS,
                           summary=summary, change_returned=change_returned)

@app.route("/play", methods=["POST"])
def play():
    denom = request.form.get("denom", "")
    outcome = game.apply(denom)
    return redirect(url_for("index"))

@app.route("/hint", methods=["POST"])
def hint():
    suggestion = game.hint()               # capture it this time!
    flash(f"💡 Try a {suggestion}.")
    return redirect(url_for("index"))

@app.route("/next", methods=["POST"])
def next_customer():
    game.start_round()
    return redirect(url_for("index"))

@app.route("/level", methods=["POST"])
def set_level():
    level = int(request.form.get("level", 1))
    game.generator.level = level
    game.start_round()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)