#!/usr/bin/env python3
"""Fax-to-Structured-Data Pipeline — receive faxes, AI extracts structured data (invoices, orders, prescriptions) into JSON."""
import os, json, time, requests, telnyx
from dotenv import load_dotenv
from flask import Flask, request, jsonify
load_dotenv()
app = Flask(__name__)
# public_key (from the Portal) lets the SDK verify inbound webhook signatures.
client = telnyx.Telnyx(api_key=os.getenv("TELNYX_API_KEY"), public_key=os.getenv("TELNYX_PUBLIC_KEY"))
TELNYX_API_KEY = os.getenv("TELNYX_API_KEY")
TELNYX_PUBLIC_KEY = os.getenv("TELNYX_PUBLIC_KEY", "")
AI_MODEL = os.getenv("AI_MODEL", "moonshotai/Kimi-K2.6")
INFERENCE_URL = "https://api.telnyx.com/v2/ai/chat/completions"
fax_queue = []
extracted_data = []

def call_inference(messages, max_tokens=600):
    resp = requests.post(INFERENCE_URL, headers={"Authorization": f"Bearer {TELNYX_API_KEY}", "Content-Type": "application/json"},
        json={"model": AI_MODEL, "messages": messages, "max_tokens": max_tokens, "temperature": 0.1}, timeout=20)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]

@app.route("/webhooks/fax", methods=["POST"])
def receive_fax():
    # Verify the Telnyx Ed25519 signature before trusting the event.
    try:
        client.webhooks.unwrap(request.get_data(as_text=True), headers=dict(request.headers))
    except Exception:
        return jsonify({"error": "invalid signature"}), 401
    payload = request.get_json()
    if not payload:
        return jsonify({"error": "invalid request body"}), 400
    data = payload.get("data", {})
    p = data.get("payload", {})
    event_type = data.get("event_type", "")
    if event_type == "fax.received":
        fax_entry = {"fax_id": p.get("fax_id"), "from": p.get("from"), "to": p.get("to"),
            "pages": p.get("page_count"), "media_url": p.get("media_url"), "status": "received",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")}
        fax_queue.append(fax_entry)
        return jsonify({"status": "queued", "fax_id": fax_entry["fax_id"]}), 200
    return jsonify({"status": "ok"}), 200

@app.route("/extract", methods=["POST"])
def extract_data():
    data = request.get_json()
    if not data:
        return jsonify({"error": "invalid request body"}), 400
    text = data.get("text", "")
    doc_type = data.get("type", "auto")
    if not text: return jsonify({"error": "text required"}), 400
    prompts = {
        "invoice": "Extract invoice data. Return JSON: vendor (string), invoice_number (string), date (string), due_date (string), line_items (list of {description, quantity, unit_price, total}), subtotal (number), tax (number), total (number), payment_terms (string).",
        "order": "Extract purchase order data. Return JSON: po_number (string), vendor (string), ship_to (string), items (list of {sku, description, quantity, unit_price}), total (number), delivery_date (string).",
        "prescription": "Extract prescription data. Return JSON: patient_name (string), prescriber (string), medication (string), dosage (string), frequency (string), quantity (number), refills (number), date (string).",
        "auto": "Identify this document type and extract all structured data. Return JSON: document_type (string), confidence (float), extracted_fields (object with all relevant key-value pairs).",
    }
    prompt = prompts.get(doc_type, prompts["auto"])
    try:
        result = call_inference([{"role": "system", "content": prompt}, {"role": "user", "content": text}])
        parsed = json.loads(result)
        parsed["extracted_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ")
        extracted_data.append(parsed)
        return jsonify(parsed), 200
    except json.JSONDecodeError:
        return jsonify({"raw": result}), 200
    except Exception as e:
        app.logger.exception("extraction failed")
        return jsonify({"error": "extraction failed"}), 500

@app.route("/faxes", methods=["GET"])
def list_faxes():
    return jsonify({"faxes": fax_queue[-50:]}), 200

@app.route("/extracted", methods=["GET"])
def list_extracted():
    return jsonify({"data": extracted_data[-50:]}), 200

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "faxes": len(fax_queue), "extracted": len(extracted_data)}), 200

if __name__ == "__main__":
    app.run(debug=False, host=os.getenv("HOST", "127.0.0.1"), port=int(os.getenv("PORT", "5000")))
