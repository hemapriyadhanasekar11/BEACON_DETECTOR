from flask import Flask, render_template, jsonify, request
from threading import Lock
from datetime import datetime
import time

app = Flask(__name__)
lock = Lock()

# The beacon must send a heartbeat more often than this timeout.
BEACON_TIMEOUT_SECONDS = 8

state = {
    "last_seen": None,
    "last_seen_epoch": None,
    "total_heartbeats": 0,
    "source_name": "Demo Beacon",
    "source_id": None,
    "events": []
}


def current_time():
    return datetime.now().strftime("%H:%M:%S")


def beacon_is_detected():
    last_seen = state["last_seen_epoch"]
    if last_seen is None:
        return False
    return (time.time() - last_seen) <= BEACON_TIMEOUT_SECONDS


@app.route("/")
def dashboard():
    return render_template("index.html")


@app.route("/api/heartbeat", methods=["POST"])
def receive_heartbeat():
    # This local demo endpoint accepts harmless JSON heartbeat events.
    data = request.get_json(silent=True) or {}
    source_name = str(data.get("source_name", "Demo Beacon"))[:60]
    source_id = str(data.get("source_id", "BEACON-001"))[:60]

    with lock:
        state["last_seen"] = current_time()
        state["last_seen_epoch"] = time.time()
        state["total_heartbeats"] += 1
        state["source_name"] = source_name
        state["source_id"] = source_id
        state["events"].insert(0, {
            "time": state["last_seen"],
            "source_name": source_name,
            "source_id": source_id,
            "status": "Heartbeat received"
        })
        state["events"] = state["events"][:30]

    return jsonify({"ok": True, "message": "Heartbeat received"})


@app.route("/api/status")
def get_status():
    with lock:
        detected = beacon_is_detected()
        last_seen = state["last_seen"]
        total = state["total_heartbeats"]
        source_name = state["source_name"]
        source_id = state["source_id"]
        events = list(state["events"])

    seconds_since = None
    if last_seen is not None:
        seconds_since = round(time.time() - state["last_seen_epoch"], 1)

    return jsonify({
        "detected": detected,
        "status": "BEACON DETECTED" if detected else "BEACON NOT DETECTED",
        "last_seen": last_seen or "Never",
        "seconds_since": seconds_since,
        "timeout_seconds": BEACON_TIMEOUT_SECONDS,
        "total_heartbeats": total,
        "source_name": source_name,
        "source_id": source_id,
        "events": events
    })


if __name__ == "__main__":
    print("Beacon monitoring server starting...")

    print(f"Beacon timeout: {BEACON_TIMEOUT_SECONDS} seconds")
    app.run(host="127.0.0.1", port=5000, debug=False, threaded=True)