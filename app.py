"""Flask adapter: exposes the count-back game as a JSON-API web app."""

import os

from flask import Flask, render_template, request, jsonify

from cashback.game import CountBackGame
from cashback.models import DENOMINATIONS

app = Flask(__name__)

# ONE game object per process (fine for a single player on one machine).
# The app loads straight into the play screen in Learning mode.
game = CountBackGame(1, mode="learning")


def game_state():
    """Everything the screen needs to draw current state."""
    return {
        "total": str(game.problem.total),
        "paid": str(game.problem.paid),
        "remaining": str(game.remaining),
        "running": str(game.running_total),
        "pieces": game.pieces_used,
        "complete": game.running_total == game.problem.paid,
    }


def has_img(name):
    """Does a sprite exist for this denomination?"""
    return os.path.exists(os.path.join(app.static_folder,
                                       "images", f"{name}.png"))


@app.route("/")
def index():
    if game.problem is None:
        game.start_round()
    return render_template("game_screen.html", game=game,
                           denoms=DENOMINATIONS, mode=game.mode,
                           has_img=has_img)


@app.route("/api/state")
def api_state():
    """Everything the screen needs to draw current state."""
    return jsonify(game_state())


@app.route("/api/play/<denom>", methods=["POST"])
def api_play(denom):
    """Apply one denomination; return outcome, state, and the hint
    (the front-end decides whether to display it, based on the toggle)."""
    outcome = game.apply(denom)
    return jsonify({
        "message": outcome.message,
        "state": game_state(),
        "hint": "" if outcome.round_complete else game.hint(),
    })


@app.route("/api/new", methods=["POST"])
def api_new():
    """Respawn: optionally switch mode and/or level, start a fresh round.
    Returns the new state so the front end can update without a reload."""
    global game
    mode = request.args.get("mode")
    level = request.args.get("level", type=int)
    if mode in ("simulation", "learning"):
        game = CountBackGame(level or game.generator.level, mode=mode)
    elif level:
        game.generator.level = level
    game.start_round()
    return jsonify({"ok": True, "state": game_state()})


if __name__ == "__main__":
    app.run(debug=True)