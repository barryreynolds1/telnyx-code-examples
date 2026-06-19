#!/usr/bin/env python3
"""AI Property Management Maintenance Line — tenants call, AI triages maintenance requests."""
import os, json, time, requests, telnyx
from dotenv import load_dotenv
from flask import Flask, request, jsonify
import threading, time as _ttl_time
load_dotenv()
app = Flask(__name__)
client = telnyx.Telnyx(api_key=os.getenv("TELNYX_API_KEY"))
TELNYX_PUBLIC_KEY = os.getenv("TELNYX_PUBLIC_KEY", "")
TELNYX_API_KEY = os.getenv("TELNYX_API_KEY")
AI_MODEL = os.getenv("AI_MODEL", "moonshotai/Kimi-K2.6")
MAINTENANCE_NUMBER = os.getenv("MAINTENANCE_NUMBER")
INFERENCE_URL = "https://api.telnyx.com/v2/ai/chat/completions"
active_calls = {}


def encode_client_state(data):
    """Encode call context for Telnyx client_state round-trip."""
    import base64, json
    return base64.b64encode(json.dumps(data).encode()).decode()

def decode_client_state(event_data):
    """Decode client_state echoed back by Telnyx webhook."""
    import base64, json
    cs = event_data.get("client_state", "")
    if not cs:
        return {}
    try:
        return json.loads(base64.b64decode(cs))
    except Exception:
        return {}

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

_start_ttl_cleanup(active_calls)

work_orders = []

SYSTEM_PROMPT = """You are a property management maintenance line. Collect:
1. Tenant name and unit number
2. Description of the issue
3. Urgency (is it an emergency like flooding/fire/no heat, or routine?)
4. Preferred access time for the maintenance team
For emergencies (water leak, no heat in winter, fire, gas smell), tell them to call 911 if danger, then assure immediate dispatch.
Keep responses under 2 sentences."""

def call_inference(messages, max_tokens=150):
    resp = requests.post(INFERENCE_URL, headers={"Authorization": f"Bearer {TELNYX_API_KEY}", "Content-Type": "application/json"},
        json={"model": AI_MODEL, "messages": messages, "max_tokens": max_tokens, "temperature": 0.5}, timeout=15)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]

@app.route("/webhooks/voice", methods=["POST"])
def handle_voice():
    payload = request.get_json()
    if not payload:
        return jsonify({"error": "invalid request body"}), 400
    event_type = payload.get("data", {}).get("event_type")
    ccid = payload.get("data", {}).get("call_control_id")
    data = payload.get("data", {})
    call = active_calls.get(ccid)
    if event_type == "call.initiated" and data.get("direction") == "incoming":
        active_calls[ccid] = {"caller": data.get("from"), "conversation": [{"role": "system", "content": SYSTEM_PROMPT}]}
        client.calls.actions.answer(ccid)
        return jsonify({"status": "answering"}), 200
    elif event_type == "call.answered":
        client.calls.actions.speak(ccid, payload="Hi, you've reached the maintenance line. Can I get your name and unit number?", voice="female", language_code="en-US")
        return jsonify({"status": "greeting"}), 200
    elif event_type == "call.speak.ended" and call:
        client.calls.actions.gather(ccid, input_type="speech", end_silence_timeout_secs=3, timeout_secs=20, language_code="en-US")
        return jsonify({"status": "listening"}), 200
    elif event_type == "call.gather.ended" and call:
        speech = data.get("speech", {}).get("result", "")
        if not speech:
            client.calls.actions.speak(ccid, payload="Sorry, I didn't catch that.", voice="female", language_code="en-US")
            return jsonify({"status": "reprompting"}), 200
        call["conversation"].append({"role": "user", "content": speech})
        response = call_inference(call["conversation"])
        call["conversation"].append({"role": "assistant", "content": response})
        client.calls.actions.speak(ccid, payload=response, voice="female", language_code="en-US")
        return jsonify({"status": "responding"}), 200
    elif event_type == "call.hangup":
        call = active_calls.pop(ccid, None)
        if call and len(call["conversation"]) > 3:
            extract = [{"role": "system", "content": "Extract work order. Return JSON: tenant_name (string), unit (string), issue (string), urgency (emergency/urgent/routine), access_time (string or null)."},
                {"role": "user", "content": chr(10).join(f"{m['role']}: {m['content']}" for m in call["conversation"] if m["role"] != "system")}]
            try:
                wo = json.loads(call_inference(extract, max_tokens=200))
                wo["caller"] = call["caller"]
                wo["timestamp"] = time.strftime("%Y-%m-%dT%H:%M:%SZ")
                work_orders.append(wo)
                if wo.get("urgency") == "emergency":
                    requests.post("https://api.telnyx.com/v2/messages", headers={"Authorization": f"Bearer {TELNYX_API_KEY}", "Content-Type": "application/json"},
                        json={"from": MAINTENANCE_NUMBER, "to": MAINTENANCE_NUMBER, "text": f"EMERGENCY: Unit {wo.get('unit', '?', timeout=10)} - {wo.get('issue', 'unknown')}"}, timeout=10)
            except Exception:
                pass
        return jsonify({"status": "ended"}), 200
    return jsonify({"status": "ok"}), 200

@app.route("/work-orders", methods=["GET"])
def list_orders():
    return jsonify({"work_orders": work_orders[-50:]}), 200

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "work_orders": len(work_orders)}), 200

if __name__ == "__main__":
    app.run(debug=False, host=os.getenv("HOST", "127.0.0.1"), port=int(os.getenv("PORT", "5000")))
