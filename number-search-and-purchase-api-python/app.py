#!/usr/bin/env python3
"""Number Search and Purchase API — search, filter, and buy phone numbers programmatically."""
import os, json, requests
from dotenv import load_dotenv
from flask import Flask, request, jsonify
load_dotenv()
app = Flask(__name__)
TELNYX_API_KEY = os.getenv("TELNYX_API_KEY")
purchases = []

@app.route("/numbers/search", methods=["GET"])
def search_numbers():
    params = {"filter[country_code]": request.args.get("country", "US"), "filter[features][]": request.args.getlist("features") or ["sms", "voice"],
        "filter[number_type]": request.args.get("type", "local"), "page[size]": int(request.args.get("limit", 10))}
    area_code = request.args.get("area_code")
    if area_code:
        params["filter[national_destination_code]"] = area_code
    contains = request.args.get("contains")
    if contains:
        params["filter[phone_number][contains]"] = contains
    try:
        resp = requests.get("https://api.telnyx.com/v2/available_phone_numbers", headers={"Authorization": f"Bearer {TELNYX_API_KEY}"}, params=params, timeout=15)
        if resp.ok:
            numbers = resp.json().get("data", [])
            return jsonify({"numbers": [{"number": n.get("phone_number"), "features": n.get("features", []), "cost": n.get("cost_information", {}), "region": n.get("region_information", [])} for n in numbers], "total": len(numbers)}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    return jsonify({"error": "Search failed"}), 500

@app.route("/numbers/purchase", methods=["POST"])
def purchase_number():
    data = request.get_json()
    numbers = data.get("phone_numbers", [])
    results = []
    for number in numbers:
        try:
            resp = requests.post("https://api.telnyx.com/v2/number_orders", headers={"Authorization": f"Bearer {TELNYX_API_KEY}", "Content-Type": "application/json"},
                json={"phone_numbers": [{"phone_number": number}]}, timeout=15)
            if resp.ok:
                order = resp.json().get("data", {})
                results.append({"number": number, "status": "ordered", "order_id": order.get("id")})
                purchases.append({"number": number, "order": order})
            else:
                results.append({"number": number, "status": "failed", "error": resp.text})
        except Exception as e:
            results.append({"number": number, "status": "error", "error": str(e)})
    return jsonify({"results": results}), 200

@app.route("/numbers/inventory", methods=["GET"])
def list_inventory():
    try:
        resp = requests.get("https://api.telnyx.com/v2/phone_numbers", headers={"Authorization": f"Bearer {TELNYX_API_KEY}"}, params={"page[size]": 100}, timeout=15)
        if resp.ok:
            return jsonify(resp.json()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    return jsonify({"error": "Failed"}), 500

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "purchases": len(purchases)}), 200

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
