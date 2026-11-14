import json
import os
import datetime
import requests
from flask import Flask, request, jsonify
from collections import deque

app = Flask(__name__)

log_storage = deque(maxlen=1000)
stats = {
    "total_received": 0,
    "by_level": {"INFO": 0, "WARNING": 0, "ERROR": 0, "CRITICAL": 0},
    "alerts_forwarded": 0,
}

LOG_FILE_PATH = "/logs/application.log"
ALERT_URL = os.environ.get("ALERT_URL", "http://alert-service:5002/alert")

def save_to_file(log_entry):
    try:
        with open(LOG_FILE_PATH, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
    except Exception as e:
        print(f"Error writing to log file: {e}", flush=True)

def forward_alert(log_entry):
    try:
        requests.post(ALERT_URL, json=log_entry, timeout=5)
        stats["alerts_forwarded"] += 1
        print(f"Alert forwarded: {log_entry['level']} - {log_entry['message']}", flush=True)
    except requests.exceptions.RequestException as e:
        print(f"Failed to forward alert: {e}", flush=True)

@app.route("/collect", methods=["POST"])
def collect():
    log_entry = request.json
    if not log_entry:
        return jsonify({"error": "No log data received"}), 400
    log_storage.append(log_entry)
    stats["total_received"] += 1
    level = log_entry.get("level", "INFO")
    if level in stats["by_level"]:
        stats["by_level"][level] += 1
    save_to_file(log_entry)
    if level in ["ERROR", "CRITICAL"]:
        forward_alert(log_entry)
    print(f"Collected [{level}]: {log_entry.get('message', 'N/A')}", flush=True)
    return jsonify({"status": "received"}), 200

@app.route("/logs", methods=["GET"])
def get_logs():
    level_filter = request.args.get("level", None)
    limit = int(request.args.get("limit", 50))
    logs = list(log_storage)
    if level_filter:
        logs = [l for l in logs if l.get("level") == level_filter.upper()]
    return jsonify({"count": len(logs[-limit:]), "logs": logs[-limit:]})

@app.route("/stats", methods=["GET"])
def get_stats():
    return jsonify({"service": "log-collector", "statistics": stats, "logs_in_memory": len(log_storage)})

@app.route("/health")
def health():
    return jsonify({"status": "running", "service": "log-collector"})

@app.route("/")
def index():
    return jsonify({"service": "Log Collector", "total_logs": stats["total_received"]})

if __name__ == "__main__":
    os.makedirs(os.path.dirname(LOG_FILE_PATH), exist_ok=True)
    print("Log Collector started!", flush=True)
    app.run(host="0.0.0.0", port=5001)
