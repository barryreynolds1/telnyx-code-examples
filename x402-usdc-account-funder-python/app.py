#!/usr/bin/env python3
"""x402 USDC Account Funder — fund your Telnyx account with USDC cryptocurrency on the Base blockchain."""
import os, json, time, requests
from dotenv import load_dotenv
from flask import Flask, request, jsonify
load_dotenv()
app = Flask(__name__)
TELNYX_API_KEY = os.getenv("TELNYX_API_KEY")
API = "https://api.telnyx.com/v2"
headers = {"Authorization": f"Bearer {TELNYX_API_KEY}", "Content-Type": "application/json"}
USDC_CONTRACT = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
BASE_CHAIN_ID = 8453
quotes = []
payments = []

@app.route("/quote", methods=["POST"])
def get_quote():
    data = request.get_json()
    if not data:
        return jsonify({"error": "invalid request body"}), 400
    amount = data.get("amount_usd", "50.00")
    try:
        resp = requests.post(f"{API}/x402/credit_account/quote", headers=headers,
            json={"amount_usd": str(amount, timeout=10)}, timeout=15)
        result = resp.json()
        result["requested_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ")
        quotes.append(result)
        return jsonify(result), resp.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/pay", methods=["POST"])
def submit_payment():
    data = request.get_json()
    if not data:
        return jsonify({"error": "invalid request body"}), 400
    quote_id = data.get("quote_id")
    payment_signature = data.get("payment_signature")
    if not quote_id or not payment_signature:
        return jsonify({"error": "quote_id and payment_signature required"}), 400
    try:
        resp = requests.post(f"{API}/x402/credit_account", headers=headers,
            json={"id": quote_id, "payment_signature": payment_signature}, timeout=30)
        result = resp.json()
        result["submitted_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ")
        payments.append(result)
        return jsonify(result), resp.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/balance", methods=["GET"])
def get_balance():
    try:
        resp = requests.get(f"{API}/balance", headers=headers, timeout=15)
        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/info", methods=["GET"])
def payment_info():
    return jsonify({"chain": "Base", "chain_id": BASE_CHAIN_ID,
        "usdc_contract": USDC_CONTRACT, "min_amount": "$5.00", "max_amount": "$10,000.00",
        "quote_expiry": "5 minutes",
        "steps": ["1. POST /quote with amount", "2. Sign payment client-side with crypto wallet",
            "3. POST /pay with quote_id and signature"]}), 200

@app.route("/quotes", methods=["GET"])
def list_quotes():
    return jsonify({"quotes": quotes[-20:]}), 200

@app.route("/payments", methods=["GET"])
def list_payments():
    return jsonify({"payments": payments[-20:]}), 200

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "quotes": len(quotes), "payments": len(payments)}), 200

if __name__ == "__main__":
    app.run(debug=False, host=os.getenv("HOST", "127.0.0.1"), port=int(os.getenv("PORT", "5000")))
