#!/usr/bin/env python3
"""Global IP Failover Monitor — monitor Global IP endpoints across regions, auto-failover between healthy endpoints."""
import os, json, time, requests, threading
from dotenv import load_dotenv
from flask import Flask, request, jsonify
import threading, time as _ttl_time
load_dotenv()
app = Flask(__name__)
TELNYX_API_KEY = os.getenv("TELNYX_API_KEY")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", 60))
API = "https://api.telnyx.com/v2"
headers = {"Authorization": f"Bearer {TELNYX_API_KEY}", "Content-Type": "application/json"}
endpoints = {}

def _start_ttl_cleanup(*stores, ttl_seconds=3600, interval=300):
    def _cleanup():
        while True:
            _ttl_time.sleep(interval)
            cutoff = _ttl_time.time() - ttl_seconds
            for store in stores:
                expired = [k for k, v in store.items()
                           if isinstance(v, dict) and v.get("_ts", _ttl_time.time()) < cutoff]
                for k in expired:
                    store.pop(k, None)
    threading.Thread(target=_cleanup, daemon=True).start()

_start_ttl_cleanup(endpoints)

failover_log = []
health_history = []

@app.route("/endpoints", methods=["GET"])
def list_endpoints():
    try:
        resp = requests.get(f"{API}/global_ip_assignments", headers=headers, timeout=15)
        data = resp.json().get("data", [])
        for ep in data:
            ep_id = ep.get("id")
            if ep_id not in endpoints:
                endpoints[ep_id] = {"id": ep_id, "ip_address": ep.get("ip_address"),
                    "region": ep.get("region"), "status": "healthy", "checks": 0, "failures": 0}
        return jsonify({"endpoints": list(endpoints.values())}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/endpoints", methods=["POST"])
def add_endpoint():
    data = request.get_json()
    if not data:
        return jsonify({"error": "invalid request body"}), 400
    ep_id = data.get("id", f"ep-{int(time.time())}")
    endpoints[ep_id] = {"id": ep_id, "ip_address": data.get("ip_address"),
        "region": data.get("region"), "status": "healthy", "checks": 0, "failures": 0}
    return jsonify({"status": "added", "endpoint": endpoints[ep_id]}), 200

@app.route("/check", methods=["POST"])
def run_health_check():
    results = []
    for ep_id, ep in endpoints.items():
        ep["checks"] += 1
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            result = sock.connect_ex((ep["ip_address"], 5060))
            sock.close()
            healthy = result == 0
        except Exception:
            healthy = False
        old_status = ep["status"]
        if not healthy:
            ep["failures"] += 1
            if ep["failures"] >= 3:
                ep["status"] = "unhealthy"
        else:
            ep["failures"] = 0
            ep["status"] = "healthy"
        if old_status != ep["status"]:
            event = {"endpoint": ep_id, "ip": ep["ip_address"], "region": ep.get("region"),
                "old_status": old_status, "new_status": ep["status"],
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")}
            failover_log.append(event)
            if ep["status"] == "unhealthy":
                healthy_eps = [e for e in endpoints.values() if e["status"] == "healthy" and e["id"] != ep_id]
                if healthy_eps:
                    event["failover_to"] = healthy_eps[0]["id"]
        results.append({"id": ep_id, "ip": ep["ip_address"], "status": ep["status"],
            "failures": ep["failures"]})
    health_history.append({"timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"), "results": results})
    return jsonify({"results": results}), 200

@app.route("/failover-log", methods=["GET"])
def get_failover_log():
    return jsonify({"log": failover_log[-50:]}), 200

@app.route("/regions", methods=["GET"])
def regions():
    try:
        resp = requests.get(f"{API}/global_ip_allowed_regions", headers=headers, timeout=15)
        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/health", methods=["GET"])
def health():
    healthy_count = sum(1 for e in endpoints.values() if e["status"] == "healthy")
    return jsonify({"status": "ok", "endpoints": len(endpoints), "healthy": healthy_count,
        "failovers": len(failover_log)}), 200

if __name__ == "__main__":
    app.run(debug=False, host=os.getenv("HOST", "127.0.0.1"), port=int(os.getenv("PORT", "5000")))
