#!/usr/bin/env python3
"""Wireless Fleet Activation Portal — bulk activate SIMs with status tracking."""
import os, json, time, requests
from dotenv import load_dotenv
from flask import Flask, request, jsonify
load_dotenv()
app = Flask(__name__)
TELNYX_API_KEY = os.getenv("TELNYX_API_KEY")
activation_log = []

@app.route("/sims", methods=["GET"])
def list_sims():
    try:
        resp = requests.get("https://api.telnyx.com/v2/sim_cards", headers={"Authorization": f"Bearer {TELNYX_API_KEY}"},
            params={"page[size]": 50}, timeout=15)
        if resp.ok:
            return jsonify(resp.json()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    return jsonify({"error": "Failed"}), 500

@app.route("/sims/activate", methods=["POST"])
def activate_sims():
    data = request.get_json()
    sim_ids = data.get("sim_ids", [])
    results = []
    for sim_id in sim_ids:
        try:
            resp = requests.patch(f"https://api.telnyx.com/v2/sim_cards/{sim_id}", headers={"Authorization": f"Bearer {TELNYX_API_KEY}", "Content-Type": "application/json"},
                json={"status": "active"}, timeout=10)
            status = "activated" if resp.ok else "failed"
            results.append({"sim_id": sim_id, "status": status})
            activation_log.append({"sim_id": sim_id, "status": status, "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")})
        except Exception as e:
            results.append({"sim_id": sim_id, "status": "error", "error": str(e)})
    return jsonify({"results": results, "activated": sum(1 for r in results if r["status"] == "activated")}), 200

@app.route("/sims/deactivate", methods=["POST"])
def deactivate_sims():
    data = request.get_json()
    sim_ids = data.get("sim_ids", [])
    results = []
    for sim_id in sim_ids:
        try:
            resp = requests.patch(f"https://api.telnyx.com/v2/sim_cards/{sim_id}", headers={"Authorization": f"Bearer {TELNYX_API_KEY}", "Content-Type": "application/json"},
                json={"status": "inactive"}, timeout=10)
            results.append({"sim_id": sim_id, "status": "deactivated" if resp.ok else "failed"})
        except Exception as e:
            results.append({"sim_id": sim_id, "status": "error"})
    return jsonify({"results": results}), 200

@app.route("/activation-log", methods=["GET"])
def get_log():
    return jsonify({"log": activation_log[-100:]}), 200

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "activations": len(activation_log)}), 200

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
