# -*- coding: utf-8 -*-
"""
Minimal Flask entry point for the Shift Management web system.

Run directly:        python app.py
Or via Flask:        flask run            (FLASK_APP=app.py)
Or via the runner:   run_local.bat / run_local.py
"""
from flask import Flask, jsonify, request, render_template

from services.firestore_service import (
    check_firestore_connection,
    get_app_state,
    save_app_state,
)

app = Flask(__name__)


@app.route("/")
def index():
    """Serve the Shift Management UI."""
    return render_template("index.html")


@app.route("/health")
def health():
    """Lightweight readiness endpoint used by the local runner."""
    return jsonify(status="ok")


@app.route("/health/firestore")
def firestore_health():
    """Verify Firestore connectivity without changing app persistence behavior."""
    try:
        check_firestore_connection()
        return jsonify(status="ok", firestore="connected")
    except Exception as exc:
        return (
            jsonify(
                status="error",
                firestore="not_connected",
                message=str(exc),
            ),
            500,
        )


@app.route("/api/state", methods=["GET"])
def api_get_state():
    """Return the full app state stored in Firestore."""
    try:
        return jsonify(state=get_app_state())
    except Exception:
        return (
            jsonify(
                status="error",
                message="Could not load app state from Firestore.",
            ),
            500,
        )


@app.route("/api/state", methods=["PUT"])
def api_save_state():
    """Save the full app state to Firestore."""
    body = request.get_json(silent=True)
    if body is None:
        return jsonify(status="error", message="Invalid JSON body."), 400

    state = body.get("state") if isinstance(body, dict) and "state" in body else body
    if not isinstance(state, dict):
        return jsonify(status="error", message="State must be a JSON object."), 400

    try:
        metadata = save_app_state(state)
        return jsonify(ok=True, **metadata)
    except ValueError:
        return jsonify(status="error", message="State must be a JSON object."), 400
    except Exception:
        return (
            jsonify(
                status="error",
                message="Could not save app state to Firestore.",
            ),
            500,
        )


if __name__ == "__main__":
    # Local-only server. debug=False to avoid the reloader spawning two
    # processes (which would make the browser-open / port checks flaky).
    app.run(host="127.0.0.1", port=5000, debug=False)
