import datetime
from flask import Flask, request, jsonify
from collections import deque

app = Flask(__name__)

alerts = deque(maxlen=500)
alert_stats = {
    "total_alerts": 0,
    "by_level": {"ERROR": 0, "CRITICAL": 0},
    "last_alert_time": None,
}
error_window = deque(maxlen=100)
pattern_alerts = deque(maxlen=100)
ALERT_THRESHOLD = 5

def check_error_pattern():
    now = datetime.datetime.now()
    cutoff = now - datetime.timedelta(seconds=60)
    recent_errors = sum(
        1 for t in error_window
        if datetime.datetime.fromisoformat(t) > cutoff
    )
    if recent_errors >= ALERT_THRESHOLD:
        pattern_alert = {
            "type": "PATTERN_DETECTED",
            "message": f"High error rate: {recent_errors} errors in last 60 seconds!",
            "timestamp": now.isoformat(),
            "error_count": recent_errors,
        }
        pattern_alerts.append(pattern_alert)
        print(f"\n{'!'*60}", flush=True)
        print(f"  PATTERN ALERT: {recent_errors} errors in 60 seconds!", flush=True)
        print(f"{'!'*60}\n", flush=True)

@app.route("/alert", methods=["POST"])
def receive_alert():
    log_entry = request.json
    if not log_entry:
        return jsonify({"error": "No data received"}), 400
    level = log_entry.get("level", "UNKNOWN")
    message = log_entry.get("message", "N/A")
    timestamp = log_entry.get("timestamp", datetime.datetime.now().isoformat())
    alert = {
        "alert_id": alert_stats["total_alerts"] + 1,
        "level": level,
        "message": message,
        "source_ip": log_entry.get("source_ip", "unknown"),
        "original_timestamp": timestamp,
        "alert_timestamp": datetime.datetime.now().isoformat(),
    }
    alerts.append(alert)
    alert_stats["total_alerts"] += 1
    alert_stats["last_alert_time"] = datetime.datetime.now().isoformat()
    if level in alert_stats["by_level"]:
        alert_stats["by_level"][level] += 1
    error_window.append(timestamp)
    if level == "CRITICAL":
        print(f"\n{'*'*60}", flush=True)
        print(f"  *** CRITICAL ALERT ***", flush=True)
        print(f"  Message : {message}", flush=True)
        print(f"  Source  : {alert['source_ip']}", flush=True)
        print(f"  Time    : {timestamp}", flush=True)
        print(f"{'*'*60}\n", flush=True)
    else:
        print(f"[ALERT] {level}: {message}", flush=True)
    check_error_pattern()
    return jsonify({"status": "alert_received", "alert_id": alert["alert_id"]}), 200

@app.route("/alerts", methods=["GET"])S
@app.route("/patterns", methods=["GET"])
def get_patterns():
    return jsonify({"pattern_alerts": list(pattern_alerts), "count": len(pattern_alerts)})

@app.route("/stats", methods=["GET"])
def get_stats():
    return jsonify({"service": "alert-service", "statistics": alert_stats})

@app.route("/health")
def health():
    return jsonify({"status": "running", "service": "alert-service"})

@app.route("/")
def index():
    return jsonify({"service": "Alert Service", "total_alerts": alert_stats["total_alerts"]})

if __name__ == "__main__":
    print("Alert Service started!", flush=True)
    app.run(host="0.0.0.0", port=5002)
