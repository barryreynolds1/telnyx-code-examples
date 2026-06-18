#!/usr/bin/env python3
"""CNAM Caller ID Lookup Enrichment — look up CNAM for inbound callers, enrich CRM records with caller identity."""
import os, json, time, requests
from dotenv import load_dotenv
from flask import Flask, request, jsonify
load_dotenv()
app = Flask(__name__)
TELNYX_API_KEY = os.getenv("TELNYX_API_KEY")
API = "https://api.telnyx.com/v2"
headers = {"Authorization": f"Bearer {TELNYX_API_KEY}", "Content-Type": "application/json"}
lookup_cache = {}
enrichment_log = []

@app.route("/lookup/<number>", methods=["GET"])
def lookup_number(number):
    if number in lookup_cache:
        return jsonify({"result": lookup_cache[number], "source": "cache"}), 200
    try:
        resp = requests.get(f"{API}/number_lookup/{number}",
            headers=headers, params={"type": "caller-name"}, timeout=15)
        data = resp.json().get("data", {})
        result = {"number": number,
            "caller_name": data.get("caller_name", {}).get("caller_name"),
            "caller_type": data.get("caller_name", {}).get("caller_type"),
            "carrier": data.get("carrier", {}).get("name"),
            "carrier_type": data.get("carrier", {}).get("type"),
            "country_code": data.get("country_code"),
            "national_format": data.get("national_format"),
            "valid": data.get("valid"),
            "portability": data.get("portability", {}).get("status"),
            "looked_up_at": time.strftime("%Y-%m-%dT%H:%M:%SZ")}
        lookup_cache[number] = result
        return jsonify({"result": result, "source": "api"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/lookup/batch", methods=["POST"])
def batch_lookup():
    data = request.get_json()
    numbers = data.get("numbers", [])
    results = []
    for num in numbers[:50]:
        try:
            resp = requests.get(f"{API}/number_lookup/{num}",
                headers=headers, params={"type": "caller-name"}, timeout=15)
            info = resp.json().get("data", {})
            results.append({"number": num,
                "caller_name": info.get("caller_name", {}).get("caller_name"),
                "carrier": info.get("carrier", {}).get("name"),
                "valid": info.get("valid")})
        except Exception:
            results.append({"number": num, "error": "lookup_failed"})
    return jsonify({"results": results, "total": len(results)}), 200

@app.route("/webhooks/voice", methods=["POST"])
def enrich_inbound():
    payload = request.get_json()
    data = payload.get("data", {})
    if data.get("event_type") == "call.initiated" and data.get("direction") == "incoming":
        caller = data.get("from", "")
        try:
            resp = requests.get(f"{API}/number_lookup/{caller}",
                headers=headers, params={"type": "caller-name"}, timeout=10)
            info = resp.json().get("data", {})
            enrichment = {"caller": caller,
                "name": info.get("caller_name", {}).get("caller_name", "Unknown"),
                "carrier": info.get("carrier", {}).get("name"),
                "type": info.get("caller_name", {}).get("caller_type"),
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")}
            enrichment_log.append(enrichment)
            return jsonify({"enrichment": enrichment}), 200
        except Exception:
            return jsonify({"caller": caller, "enrichment": "failed"}), 200
    return jsonify({"status": "ok"}), 200

@app.route("/enrichments", methods=["GET"])
def list_enrichments():
    return jsonify({"enrichments": enrichment_log[-50:]}), 200

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "cached": len(lookup_cache), "enrichments": len(enrichment_log)}), 200

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
