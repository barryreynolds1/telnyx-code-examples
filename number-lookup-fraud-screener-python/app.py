#!/usr/bin/env python3
"""Number Lookup Fraud Screener — screen inbound calls/messages for fraud indicators using number lookup before connecting."""
import os, json, time, requests
from dotenv import load_dotenv
from flask import Flask, request, jsonify
load_dotenv()
app = Flask(__name__)
TELNYX_API_KEY = os.getenv("TELNYX_API_KEY")
TELNYX_PUBLIC_KEY = os.getenv("TELNYX_PUBLIC_KEY", "")
API = "https://api.telnyx.com/v2"
headers = {"Authorization": f"Bearer {TELNYX_API_KEY}", "Content-Type": "application/json"}
screening_log = []
blocked_numbers = set()

RISK_RULES = {"voip_carrier": 2, "prepaid": 3, "no_cnam": 1, "recently_ported": 2,
    "toll_free": 1, "international": 2}

def calculate_risk(lookup_data):
    score = 0
    factors = []
    carrier = lookup_data.get("carrier", {})
    caller_name = lookup_data.get("caller_name", {})
    if carrier.get("type") == "voip":
        score += RISK_RULES["voip_carrier"]
        factors.append("VoIP carrier")
    if carrier.get("type") == "prepaid":
        score += RISK_RULES["prepaid"]
        factors.append("Prepaid number")
    if not caller_name.get("caller_name"):
        score += RISK_RULES["no_cnam"]
        factors.append("No CNAM registered")
    portability = lookup_data.get("portability", {})
    if portability.get("status") == "ported":
        score += RISK_RULES["recently_ported"]
        factors.append("Recently ported")
    if not lookup_data.get("country_code", "").startswith("US"):
        score += RISK_RULES["international"]
        factors.append("International origin")
    risk_level = "low" if score <= 2 else "medium" if score <= 4 else "high"
    return {"score": score, "level": risk_level, "factors": factors,
        "action": "block" if score >= 6 else "flag" if score >= 4 else "allow"}

@app.route("/screen/<number>", methods=["GET"])
def screen_number(number):
    if number in blocked_numbers:
        return jsonify({"number": number, "action": "block", "reason": "blocklisted"}), 200
    try:
        resp = requests.get(f"{API}/number_lookup/{number}",
            headers=headers, params={"type": "caller-name"}, timeout=15)
        lookup = resp.json().get("data", {})
        risk = calculate_risk(lookup)
        entry = {"number": number, "risk": risk, "carrier": lookup.get("carrier", {}).get("name"),
            "cnam": lookup.get("caller_name", {}).get("caller_name"),
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")}
        screening_log.append(entry)
        return jsonify(entry), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/webhooks/voice", methods=["POST"])
def screen_inbound_call():
    payload = request.get_json()
    if not payload:
        return jsonify({"error": "invalid request body"}), 400
    data = payload.get("data", {})
    if data.get("event_type") == "call.initiated" and data.get("direction") == "incoming":
        caller = data.get("from", "")
        if caller in blocked_numbers:
            screening_log.append({"number": caller, "action": "blocked", "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")})
            return jsonify({"action": "reject"}), 200
        try:
            resp = requests.get(f"{API}/number_lookup/{caller}", headers=headers,
                params={"type": "caller-name"}, timeout=5)
            lookup = resp.json().get("data", {})
            risk = calculate_risk(lookup)
            screening_log.append({"number": caller, "risk": risk, "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")})
            if risk["action"] == "block":
                blocked_numbers.add(caller)
                return jsonify({"action": "reject", "risk": risk}), 200
        except Exception:
            pass
    return jsonify({"action": "allow"}), 200

@app.route("/blocklist", methods=["POST"])
def add_to_blocklist():
    data = request.get_json()
    if not data:
        return jsonify({"error": "invalid request body"}), 400
    number = data.get("number")
    blocked_numbers.add(number)
    return jsonify({"status": "blocked", "number": number}), 200

@app.route("/blocklist", methods=["GET"])
def list_blocklist():
    return jsonify({"blocked": list(blocked_numbers)}), 200

@app.route("/screening-log", methods=["GET"])
def get_log():
    risk_filter = request.args.get("risk")
    results = screening_log[-50:]
    if risk_filter:
        results = [s for s in results if s.get("risk", {}).get("level") == risk_filter]
    return jsonify({"log": results}), 200

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "screened": len(screening_log), "blocked": len(blocked_numbers)}), 200

if __name__ == "__main__":
    app.run(debug=False, host=os.getenv("HOST", "127.0.0.1"), port=int(os.getenv("PORT", "5000")))
