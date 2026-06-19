"""
Meridian Honeypot Dashboard — Flask + SSE
11 tracking modules covering all four services.
"""

import json
import time
import queue
import threading
import logging
from datetime import datetime
from flask import Flask, Response, render_template, jsonify, request
from flask_cors import CORS
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from honeypot.db import DB
from honeypot.mitre import score_sophistication

logger = logging.getLogger("dashboard")

app = Flask(__name__)
CORS(app)

db = DB()
_event_queue = queue.Queue(maxsize=500)


def push_event(event: dict):
    try:
        _event_queue.put_nowait(event)
    except queue.Full:
        pass


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/events")
def sse_stream():
    def generate():
        yield "data: {\"type\": \"connected\"}\n\n"
        while True:
            try:
                event = _event_queue.get(timeout=30)
                yield f"data: {json.dumps(event)}\n\n"
            except queue.Empty:
                yield "data: {\"type\": \"ping\"}\n\n"
    return Response(generate(), mimetype="text/event-stream",
                    headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@app.route("/api/stats")
def api_stats():
    return jsonify(db.get_stats())


@app.route("/api/sessions")
def api_sessions():
    limit = int(request.args.get("limit", 50))
    return jsonify(db.get_recent_sessions(limit))


@app.route("/api/countries")
def api_countries():
    return jsonify(db.get_top_countries())


@app.route("/api/credentials")
def api_credentials():
    return jsonify(db.get_top_credentials())


@app.route("/api/asns")
def api_asns():
    return jsonify(db.get_top_asns())


@app.route("/api/services")
def api_services():
    return jsonify(db.get_service_breakdown())


@app.route("/api/hourly")
def api_hourly():
    return jsonify(db.get_hourly_volume())


@app.route("/api/mitre")
def api_mitre():
    return jsonify(db.get_mitre_summary())


@app.route("/api/high-interest")
def api_high_interest():
    return jsonify(db.get_high_interest_sessions())


@app.route("/api/sophistication")
def api_sophistication():
    return jsonify(db.get_sophistication_distribution())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)
