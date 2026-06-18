#!/usr/bin/env python3
"""Call Whisper & Screen Pop — whisper caller info to agent before connecting the call."""
import os, json, time, requests, telnyx
from dotenv import load_dotenv
from flask import Flask, request, jsonify
import threading, time as _ttl_time
load_dotenv()
app = Flask(__name__)
client = telnyx.Telnyx(api_key=os.getenv("TELNYX_API_KEY"))
TELNYX_PUBLIC_KEY = os.getenv("TELNYX_PUBLIC_KEY", "")
TELNYX_API_KEY = os.getenv("TELNYX_API_KEY")
MAIN_NUMBER = os.getenv("MAIN_NUMBER")
AGENT_NUMBER = os.getenv("AGENT_NUMBER")
CONNECTION_ID = os.getenv("CONNECTION_ID")
contacts_db = {"+15551234567": {"name": "Jane Smith", "company": "Acme Corp", "tier": "Enterprise", "last_call": "2 weeks ago", "open_tickets": 2},
    "+15559876543": {"name": "Bob Johnson", "company": "Startup Inc", "tier": "Growth", "last_call": "yesterday", "open_tickets": 0}}
active_calls = {}

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

call_log = []

def lookup_caller(phone):
    if phone in contacts_db:
        return contacts_db[phone]
    try:
        resp = requests.get(f"https://api.telnyx.com/v2/number_lookup/{phone}", headers={"Authorization": f"Bearer {TELNYX_API_KEY}"}, timeout=10)
        if resp.ok:
            data = resp.json().get("data", {})
            return {"name": data.get("caller_name", {}).get("caller_name", "Unknown"), "carrier": data.get("carrier", {}).get("name"), "type": data.get("phone_number", {}).get("type")}
    except Exception:
        pass
    return {"name": "Unknown caller"}

@app.route("/webhooks/voice", methods=["POST"])
def handle_voice():
    payload = request.get_json()
    if not payload:
        return jsonify({"error": "invalid request body"}), 400
    event_type = payload.get("data", {}).get("event_type")
    ccid = payload.get("data", {}).get("call_control_id")
    data = payload.get("data", {})
    if event_type == "call.initiated" and data.get("direction") == "incoming":
        caller = data.get("from", "unknown")
        caller_info = lookup_caller(caller)
        active_calls[ccid] = {"caller": caller, "info": caller_info, "state": "holding"}
        client.calls.actions.answer(ccid)
        return jsonify({"status": "answering"}), 200
    elif event_type == "call.answered":
        call = active_calls.get(ccid)
        if call:
            client.calls.actions.speak(ccid, payload="One moment please while we connect you.", voice="female", language_code="en-US")
            try:
                agent_resp = requests.post("https://api.telnyx.com/v2/calls", headers={"Authorization": f"Bearer {TELNYX_API_KEY}", "Content-Type": "application/json"},
                    json={"to": AGENT_NUMBER, "from": MAIN_NUMBER, "connection_id": CONNECTION_ID}, timeout=10)
                agent_ccid = agent_resp.json().get("data", {}).get("call_control_id")
                if agent_ccid:
                    call["agent_ccid"] = agent_ccid
                    active_calls[agent_ccid] = {"type": "agent_leg", "original_ccid": ccid}
            except Exception:
                pass
        return jsonify({"status": "connecting"}), 200
    elif event_type == "call.answered" and ccid in active_calls and active_calls[ccid].get("type") == "agent_leg":
        original = active_calls[ccid]["original_ccid"]
        orig_call = active_calls.get(original, {})
        info = orig_call.get("info", {})
        whisper = f"Incoming call from {info.get('name', 'unknown')}"
        if info.get("company"):
            whisper += f" at {info['company']}"
        if info.get("tier"):
            whisper += f", {info['tier']} tier"
        if info.get("open_tickets"):
            whisper += f", {info['open_tickets']} open tickets"
        client.calls.actions.speak(ccid, payload=whisper, voice="female", language_code="en-US")
        return jsonify({"status": "whispering"}), 200
    elif event_type == "call.speak.ended":
        call = active_calls.get(ccid)
        if call and call.get("type") == "agent_leg":
            original = call["original_ccid"]
            try:
                client.calls.actions.bridge(ccid, call_control_id=original)
            except Exception:
                pass
        return jsonify({"status": "ok"}), 200
    elif event_type == "call.hangup":
        call = active_calls.pop(ccid, None)
        if call:
            call_log.append({"caller": call.get("caller", ""), "info": call.get("info", {}), "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")})
        return jsonify({"status": "ended"}), 200
    return jsonify({"status": "ok"}), 200

@app.route("/contacts", methods=["POST"])
def add_contact():
    data = request.get_json()
    if not data:
        return jsonify({"error": "invalid request body"}), 400
    phone = data.get("phone")
    contacts_db[phone] = {k: v for k, v in data.items() if k != "phone"}
    return jsonify({"status": "added"}), 200

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "contacts": len(contacts_db), "active": len(active_calls)}), 200

if __name__ == "__main__":
    app.run(debug=False, host=os.getenv("HOST", "127.0.0.1"), port=int(os.getenv("PORT", "5000")))
