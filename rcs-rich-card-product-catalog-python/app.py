#!/usr/bin/env python3
"""RCS Rich Card Product Catalog — AI-powered product recommendations with rich cards and carousels."""

import os, json, requests
from dotenv import load_dotenv
from flask import Flask, request, jsonify
import threading, time as _ttl_time

load_dotenv()
app = Flask(__name__)

TELNYX_API_KEY = os.getenv("TELNYX_API_KEY")
TELNYX_PUBLIC_KEY = os.getenv("TELNYX_PUBLIC_KEY", "")
AI_MODEL = os.getenv("AI_MODEL", "moonshotai/Kimi-K2.6")
BOT_NUMBER = os.getenv("BOT_NUMBER")
MESSAGING_PROFILE_ID = os.getenv("MESSAGING_PROFILE_ID")
INFERENCE_URL = "https://api.telnyx.com/v2/ai/chat/completions"

PRODUCT_CATALOG = [
    {"id": "voice-api", "name": "Voice API", "desc": "Programmable voice with global reach", "price": "Starting $0.005/min", "image": "https://telnyx.com/og/voice.png", "url": "https://telnyx.com/voice-api"},
    {"id": "sms-api", "name": "SMS API", "desc": "Global SMS with 99.5% deliverability", "price": "Starting $0.004/msg", "image": "https://telnyx.com/og/messaging.png", "url": "https://telnyx.com/messaging"},
    {"id": "inference", "name": "AI Inference", "desc": "LLM inference on Telnyx GPUs", "price": "Starting $0.60/M tokens", "image": "https://telnyx.com/og/inference.png", "url": "https://telnyx.com/inference"},
    {"id": "sip", "name": "SIP Trunking", "desc": "Enterprise SIP with elastic capacity", "price": "Starting $0.005/min", "image": "https://telnyx.com/og/sip.png", "url": "https://telnyx.com/sip-trunks"},
]

conversations = {}

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

_start_ttl_cleanup(conversations)


def call_inference(messages, max_tokens=200):
    resp = requests.post(INFERENCE_URL, headers={"Authorization": f"Bearer {TELNYX_API_KEY}", "Content-Type": "application/json"},
        json={"model": AI_MODEL, "messages": messages, "max_tokens": max_tokens, "temperature": 0.7}, timeout=15)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]

def send_rcs_message(to, text, suggestions=None):
    payload = {"from": BOT_NUMBER, "to": to, "text": text, "messaging_profile_id": MESSAGING_PROFILE_ID, "type": "rcs"}
    if suggestions:
        payload["suggestions"] = suggestions
    try:
        requests.post("https://api.telnyx.com/v2/messages", headers={"Authorization": f"Bearer {TELNYX_API_KEY}", "Content-Type": "application/json"}, json=payload, timeout=10)
    except requests.RequestException as e:
        app.logger.error("RCS send failed: %s", e)

def recommend_products(query):
    catalog_str = json.dumps(PRODUCT_CATALOG)
    messages = [{"role": "system", "content": f"You are a product recommendation assistant. Available products: {catalog_str}. Based on the query, return JSON array of matching product IDs (max 3). Also include a brief recommendation message."},
        {"role": "user", "content": query}]
    return call_inference(messages)

@app.route("/webhooks/messaging", methods=["POST"])
def handle_rcs():
    payload = request.get_json()
    if not payload:
        return jsonify({"error": "invalid request body"}), 400
    data = payload.get("data", {})
    if data.get("event_type") != "message.received" or data.get("direction") != "inbound":
        return jsonify({"status": "ignored"}), 200
    from_number = data.get("from", {}).get("phone_number", "")
    text = data.get("text", "").strip()
    if not from_number or not text:
        return jsonify({"status": "ignored"}), 200

    if text.lower() in ["menu", "products", "catalog"]:
        for product in PRODUCT_CATALOG:
            send_rcs_message(from_number, f"{product['name']}\n{product['desc']}\n{product['price']}",
                suggestions=[{"type": "action", "text": f"Learn more about {product['name']}", "url": product['url']}])
        return jsonify({"status": "catalog_sent"}), 200

    try:
        rec_json = recommend_products(text)
        rec = json.loads(rec_json) if isinstance(rec_json, str) else rec_json
        message = rec.get("message", "Here are my recommendations:") if isinstance(rec, dict) else "Based on your needs:"
        send_rcs_message(from_number, message)
        product_ids = rec.get("products", rec) if isinstance(rec, dict) else rec
        if isinstance(product_ids, list):
            for pid in product_ids[:3]:
                product = next((p for p in PRODUCT_CATALOG if p["id"] == pid), None)
                if product:
                    send_rcs_message(from_number, f"{product['name']}\n{product['desc']}\n{product['price']}",
                        suggestions=[{"type": "action", "text": "View details", "url": product["url"]}])
    except Exception:
        send_rcs_message(from_number, "I can help you find the right product. Try asking about voice, messaging, AI, or SIP.")
    return jsonify({"status": "recommended"}), 200

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "products": len(PRODUCT_CATALOG)}), 200

if __name__ == "__main__":
    app.run(debug=False, host=os.getenv("HOST", "127.0.0.1"), port=int(os.getenv("PORT", "5000")))
