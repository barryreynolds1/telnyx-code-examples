#!/usr/bin/env python3
"""AI Appointment Booking SMS Flow — guided SMS booking with available slot selection."""
import os, json, time, requests, telnyx
from dotenv import load_dotenv
from flask import Flask, request, jsonify
import threading, time as _ttl_time
load_dotenv()
app = Flask(__name__)
client = telnyx.Telnyx(api_key=os.getenv("TELNYX_API_KEY"), public_key=os.getenv("TELNYX_PUBLIC_KEY"))
TELNYX_API_KEY = os.getenv("TELNYX_API_KEY")
TELNYX_PUBLIC_KEY = os.getenv("TELNYX_PUBLIC_KEY", "")
AI_MODEL = os.getenv("AI_MODEL", "moonshotai/Kimi-K2.6")
BOOKING_NUMBER = os.getenv("BOOKING_NUMBER")
MESSAGING_PROFILE_ID = os.getenv("MESSAGING_PROFILE_ID", "")
INFERENCE_URL = "https://api.telnyx.com/v2/ai/chat/completions"
slots = [{"id": 1, "day": "Monday", "time": "10:00 AM", "available": True}, {"id": 2, "day": "Monday", "time": "2:00 PM", "available": True},
    {"id": 3, "day": "Tuesday", "time": "9:00 AM", "available": True}, {"id": 4, "day": "Wednesday", "time": "11:00 AM", "available": True},
    {"id": 5, "day": "Thursday", "time": "3:00 PM", "available": True}, {"id": 6, "day": "Friday", "time": "10:00 AM", "available": True}]
sessions = {}

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

_start_ttl_cleanup(sessions)

bookings = []

def send_sms(to, text):
    try:
        requests.post("https://api.telnyx.com/v2/messages", headers={"Authorization": f"Bearer {TELNYX_API_KEY}", "Content-Type": "application/json"},
            json={"from": BOOKING_NUMBER, "to": to, "text": text, "messaging_profile_id": MESSAGING_PROFILE_ID}, timeout=10)
    except Exception as e:
        app.logger.error("SMS failed: %s", e)

@app.route("/webhooks/messaging", methods=["POST"])
def handle_sms():
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
    if data.get("event_type") != "message.received" or p.get("direction") != "inbound":
        return jsonify({"status": "ignored"}), 200
    phone = p.get("from", {}).get("phone_number", "")
    text = p.get("text", "").strip()
    if not phone: return jsonify({"status": "ignored"}), 200
    session = sessions.get(phone, {"step": "start"})
    if text.upper() == "BOOK" or session["step"] == "start":
        avail = [s for s in slots if s["available"]]
        if not avail:
            send_sms(phone, "Sorry, no slots available right now. Check back later!")
            return jsonify({"status": "no_slots"}), 200
        msg = "Available times:\n" + chr(10).join(f"{s['id']}. {s['day']} {s['time']}" for s in avail) + "\n\nReply with the number to book."
        send_sms(phone, msg)
        sessions[phone] = {"step": "choose_slot"}
        return jsonify({"status": "showing_slots"}), 200
    elif session["step"] == "choose_slot":
        try:
            slot_id = int(text)
            slot = next((s for s in slots if s["id"] == slot_id and s["available"]), None)
            if slot:
                sessions[phone] = {"step": "confirm_name", "slot": slot}
                send_sms(phone, f"Great! {slot['day']} at {slot['time']}. What name should I book under?")
            else:
                send_sms(phone, "That slot isn't available. Reply with a valid number.")
        except ValueError:
            send_sms(phone, "Reply with the slot number (e.g., 1, 2, 3).")
        return jsonify({"status": "processing"}), 200
    elif session["step"] == "confirm_name":
        slot = session["slot"]
        slot["available"] = False
        booking = {"name": text, "slot": slot, "phone": phone, "booked_at": time.strftime("%Y-%m-%dT%H:%M:%SZ")}
        bookings.append(booking)
        send_sms(phone, f"Booked! {text}, {slot['day']} at {slot['time']}. Reply CANCEL to cancel or BOOK for another slot.")
        sessions[phone] = {"step": "start"}
        return jsonify({"status": "booked"}), 200
    return jsonify({"status": "ok"}), 200

@app.route("/bookings", methods=["GET"])
def list_bookings():
    return jsonify({"bookings": bookings}), 200

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "bookings": len(bookings), "available": sum(1 for s in slots if s["available"])}), 200

if __name__ == "__main__":
    app.run(debug=False, host=os.getenv("HOST", "127.0.0.1"), port=int(os.getenv("PORT", "5000")))
