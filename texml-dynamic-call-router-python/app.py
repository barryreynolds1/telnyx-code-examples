#!/usr/bin/env python3
"""TeXML Dynamic Call Router — time-of-day and caller-based routing with TeXML responses."""
import os, json, time
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, request, Response, jsonify
import threading, time as _ttl_time
load_dotenv()
app = Flask(__name__)
BUSINESS_HOURS_NUMBER = os.getenv("BUSINESS_HOURS_NUMBER", "+15551234567")
AFTER_HOURS_NUMBER = os.getenv("AFTER_HOURS_NUMBER", "+15559876543")
VOICEMAIL_URL = os.getenv("VOICEMAIL_URL", "https://example.com/voicemail.mp3")
vip_callers = {}

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

_start_ttl_cleanup(vip_callers)

call_log = []

@app.route("/texml/route", methods=["POST"])
def route_call():
    caller = request.form.get("From", "")
    called = request.form.get("To", "")
    now = datetime.utcnow()
    hour = now.hour
    is_business_hours = 14 <= hour <= 23  # 9am-6pm ET in UTC
    is_vip = caller in vip_callers
    call_log.append({"caller": caller, "called": called, "time": now.isoformat(), "business_hours": is_business_hours, "vip": is_vip})
    if is_vip:
        texml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response><Say voice="female">Welcome back, valued customer. Connecting you now.</Say><Dial><Number>{BUSINESS_HOURS_NUMBER}</Number></Dial></Response>"""
    elif is_business_hours:
        texml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response><Say voice="female">Thank you for calling. Please hold while we connect you.</Say><Dial timeout="30"><Number>{BUSINESS_HOURS_NUMBER}</Number></Dial><Say>Sorry, no one is available. Please leave a message.</Say><Record maxLength="120" action="/texml/recording"/></Response>"""
    else:
        texml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response><Say voice="female">Our office is currently closed. Business hours are 9 AM to 6 PM Eastern. Please leave a message and we will return your call.</Say><Record maxLength="120" action="/texml/recording"/></Response>"""
    return Response(texml, mimetype="application/xml")

@app.route("/texml/recording", methods=["POST"])
def handle_recording():
    texml = """<?xml version="1.0" encoding="UTF-8"?>
<Response><Say>Thank you. Goodbye.</Say><Hangup/></Response>"""
    return Response(texml, mimetype="application/xml")

@app.route("/vip", methods=["POST"])
def add_vip():
    data = request.get_json()
    if not data:
        return jsonify({"error": "invalid request body"}), 400
    phone = data.get("phone_number")
    vip_callers[phone] = {"name": data.get("name", ""), "added": time.time()}
    return jsonify({"status": "added", "phone": phone}), 200

@app.route("/calls", methods=["GET"])
def list_calls():
    return jsonify({"calls": call_log[-50:]}), 200

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "calls": len(call_log), "vips": len(vip_callers)}), 200

if __name__ == "__main__":
    app.run(debug=False, host=os.getenv("HOST", "127.0.0.1"), port=int(os.getenv("PORT", "5000")))
