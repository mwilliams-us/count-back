"""Flask adapter: exposes the count-back game as a clickable web app."""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from cashback.game import CountBackGame
from cashback.models import DENOMINATIONS

app = Flask(__name__)
app.secret_key = "countback-dev"   # needed for flash messages; change in production

# ONE game object per process (fine for a single player on one machine)
game = CountBackGame(1)

import os

@app.route("/")
def index():
    if game.problem is None:
        game.start_round()

    def has_img(name):
        return os.path.exists(os.path.join(app.static_folder,
                                           "images", f"{name}.png"))

    return render_template("game_screen.html", game=game,
                           denoms=DENOMINATIONS, has_img=has_img)

@app.route("/menu")
def main_menu():
    return render_template("main_menu.html")

@app.route("/game")
def game_screen():
    # Ensure we have a problem
    if game.problem is None:
        game.start_round()
    return render_template("game_screen.html", game=game, denoms=DENOMINATIONS)

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

@app.route("/api/state")
def api_state():
    """Everything the screen needs to draw current state."""
    return jsonify({
        "total": str(game.problem.total),
        "paid": str(game.problem.paid),
        "remaining": str(game.remaining),
        "running": str(game.running_total),
        "pieces": game.pieces_used,
        "complete": game.running_total == game.problem.paid,
    })

@app.route("/api/play/<denom>", methods=["POST"])
def api_play(denom):
    """Apply one denomination; return the outcome plus fresh state."""
    outcome = game.apply(denom)
    state = {
        "total": str(game.problem.total),
        "paid": str(game.problem.paid),
        "remaining": str(game.remaining),
        "running": str(game.running_total),
        "pieces": game.pieces_used,
        "complete": game.running_total == game.problem.paid,
    }
    return jsonify({"message": outcome.message, "state": state})

@app.route("/api/new", methods=["POST"])
def api_new():
    level = request.args.get("level", type=int)
    if level:
        game.generator.level = level
    game.start_round()
    return jsonify({"ok": True})

if __name__ == "__main__":
    app.run(debug=True)

    