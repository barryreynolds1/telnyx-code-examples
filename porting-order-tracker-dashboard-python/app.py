#!/usr/bin/env python3
"""Porting Order Tracker Dashboard — submit and track number porting orders with status webhook updates."""
import os, json, time, requests
from dotenv import load_dotenv
from flask import Flask, request, jsonify
load_dotenv()
app = Flask(__name__)
TELNYX_API_KEY = os.getenv("TELNYX_API_KEY")
API = "https://api.telnyx.com/v2"
headers = {"Authorization": f"Bearer {TELNYX_API_KEY}", "Content-Type": "application/json"}
local_orders = []
status_updates = []

@app.route("/porting/orders", methods=["POST"])
def submit_porting_order():
    data = request.get_json()
    try:
        resp = requests.post(f"{API}/porting_orders", headers=headers,
            json={"phone_numbers": data.get("phone_numbers", []),
                "authorized_person": data.get("authorized_person"),
                "current_provider": data.get("current_provider"),
                "billing_phone_number": data.get("billing_phone_number"),
                "customer_reference": data.get("reference", "")}, timeout=15)
        result = resp.json()
        local_orders.append({"id": result.get("data", {}).get("id"),
            "numbers": data.get("phone_numbers"),
            "provider": data.get("current_provider"),
            "status": "submitted",
            "submitted_at": time.strftime("%Y-%m-%dT%H:%M:%SZ")})
        return jsonify(result), resp.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/porting/orders", methods=["GET"])
def list_orders():
    try:
        resp = requests.get(f"{API}/porting_orders", headers=headers, timeout=15)
        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        return jsonify({"error": str(e), "local": local_orders}), 500

@app.route("/porting/orders/<order_id>", methods=["GET"])
def get_order(order_id):
    try:
        resp = requests.get(f"{API}/porting_orders/{order_id}", headers=headers, timeout=15)
        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/porting/orders/<order_id>/loa", methods=["POST"])
def upload_loa(order_id):
    data = request.get_json()
    return jsonify({"order_id": order_id,
        "instructions": "Upload LOA document via the portal or POST multipart/form-data to /v2/porting_orders/{id}/loa",
        "loa_url": data.get("loa_url", "pending")}), 200

@app.route("/webhooks/porting", methods=["POST"])
def handle_porting_webhook():
    payload = request.get_json()
    data = payload.get("data", {})
    event_type = data.get("event_type", "")
    update = {"event": event_type, "order_id": data.get("porting_order_id"),
        "status": data.get("status"), "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "details": data.get("description", "")}
    status_updates.append(update)
    for order in local_orders:
        if order["id"] == data.get("porting_order_id"):
            order["status"] = data.get("status", order["status"])
    return jsonify({"status": "received"}), 200

@app.route("/porting/updates", methods=["GET"])
def list_updates():
    return jsonify({"updates": status_updates[-50:]}), 200

@app.route("/porting/dashboard", methods=["GET"])
def dashboard():
    by_status = {}
    for order in local_orders:
        s = order.get("status", "unknown")
        by_status[s] = by_status.get(s, 0) + 1
    return jsonify({"total_orders": len(local_orders), "by_status": by_status,
        "recent_updates": status_updates[-10:]}), 200

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "orders": len(local_orders), "updates": len(status_updates)}), 200

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
