#!/usr/bin/env python3
"""Number Lookup Lead Enrichment — CNAM and carrier lookup to qualify and enrich sales leads."""
import os, json, requests
from dotenv import load_dotenv
from flask import Flask, request, jsonify
load_dotenv()
app = Flask(__name__)
TELNYX_API_KEY = os.getenv("TELNYX_API_KEY")
AI_MODEL = os.getenv("AI_MODEL", "moonshotai/Kimi-K2.6")
INFERENCE_URL = "https://api.telnyx.com/v2/ai/chat/completions"
enriched_leads = []

def lookup_number(phone):
    try:
        resp = requests.get(f"https://api.telnyx.com/v2/number_lookup/{phone}", headers={"Authorization": f"Bearer {TELNYX_API_KEY}"}, timeout=10)
        if resp.ok:
            return resp.json().get("data", {})
    except Exception:
        pass
    return {}

def call_inference(messages, max_tokens=200):
    resp = requests.post(INFERENCE_URL, headers={"Authorization": f"Bearer {TELNYX_API_KEY}", "Content-Type": "application/json"},
        json={"model": AI_MODEL, "messages": messages, "max_tokens": max_tokens, "temperature": 0.3}, timeout=15)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]

@app.route("/enrich", methods=["POST"])
def enrich_lead():
    data = request.get_json()
    phone = data.get("phone_number")
    if not phone:
        return jsonify({"error": "phone_number required"}), 400
    lookup = lookup_number(phone)
    carrier = lookup.get("carrier", {})
    cnam = lookup.get("caller_name", {})
    enrichment = {"phone": phone, "carrier_name": carrier.get("name"), "carrier_type": carrier.get("type"), "caller_name": cnam.get("caller_name"), "line_type": lookup.get("phone_number", {}).get("type"), "country": lookup.get("country_code")}
    msgs = [{"role": "system", "content": "Score this lead based on phone data. Return JSON: lead_quality (hot/warm/cold), reasoning (string), is_mobile (boolean), is_voip (boolean), recommended_channel (sms/voice/email)."},
        {"role": "user", "content": json.dumps(enrichment)}]
    try:
        score = json.loads(call_inference(msgs))
        enrichment["score"] = score
    except Exception:
        pass
    enriched_leads.append(enrichment)
    return jsonify(enrichment), 200

@app.route("/enrich/bulk", methods=["POST"])
def enrich_bulk():
    data = request.get_json()
    numbers = data.get("phone_numbers", [])
    results = []
    for phone in numbers[:50]:
        lookup = lookup_number(phone)
        results.append({"phone": phone, "carrier": lookup.get("carrier", {}).get("name"), "type": lookup.get("phone_number", {}).get("type")})
    return jsonify({"results": results, "total": len(results)}), 200

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "enriched": len(enriched_leads)}), 200

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
