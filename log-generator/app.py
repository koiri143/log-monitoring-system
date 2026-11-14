import time
import random
import datetime
import requests
import os
import threading
from flask import Flask, jsonify

app = Flask(__name__)

LOG_LEVELS = ["INFO", "INFO", "INFO", "INFO", "WARNING", "WARNING", "ERROR", "CRITICAL"]

LOG_MESSAGES = {
    "INFO": [
        "User login successful",
        "Page loaded in 120ms",
        "Database query completed",
        "Cache hit for session data",
        "API request processed successfully",
        "Health check passed",
    ],
    "WARNING": [
        "High memory usage detected: 85%",
        "API response time slow: 2500ms",
        "Disk usage above 75%",
        "Rate limit approaching for IP 192.168.1.105",
    ],
    "ERROR": [
        "Database connection failed",
        "NullPointerException in UserService",
        "Authentication token expired",
        "Payment processing failed",
    ],
    "CRITICAL": [
        "System out of memory",
        "Database server unreachable",
        "Security breach detected",
        "Application crash - core dump generated",
    ],
}

COLLECTOR_URL = os.environ.get("COLLECTOR_URL", "http://log-collector:5001/collect")
generated_count = 0
error_count = 0

def generate_log():
    global generated_count, error_count
    level = random.choice(LOG_LEVELS)
    message = random.choice(LOG_MESSAGES[level])
    timestamp = datetime.datetime.now().isoformat()
    source_ip = f"10.0.0.{random.randint(2, 254)}"
    log_entry = {
        "timestamp": timestamp,
        "level": level,
        "message": message,
        "service": "web-application",
        "source_ip": source_ip,
        "container_id": os.environ.get("HOSTNAME", "unknown"),
    }
    generated_count += 1
    if level in ["ERROR", "CRITICAL"]:
        error_count += 1
    return log_entry

def send_logs():
    while True:
        log_entry = generate_log()
        level = log_entry["level"]
        print(f"[{log_entry['timestamp']}] {level}: {log_entry['message']}", flush=True)
        try:
            requests.post(COLLECTOR_URL, json=log_entry, timeout=5)
        except requests.exceptions.RequestException as e:
            print(f"Failed to send log to collector: {e}", flush=True)
        time.sleep(random.uniform(0.5, 3.0))

@app.route("/health")
def health():
    return jsonify({"status": "running", "service": "log-generator", "logs_generated": generated_count})

@app.route("/")
def index():
    return jsonify({"service": "Log Generator", "logs_generated": generated_count})

if __name__ == "__main__":
    log_thread = threading.Thread(target=send_logs, daemon=True)
    log_thread.start()
    print("Log Generator started!", flush=True)
    app.run(host="0.0.0.0", port=5000)
