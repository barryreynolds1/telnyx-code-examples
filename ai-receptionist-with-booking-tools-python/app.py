#!/usr/bin/env python3
"""AI Receptionist with Booking Tools — AI Assistant with tool_use for real calendar booking actions."""
import os, json, time, requests
from dotenv import load_dotenv
from flask import Flask, request, jsonify
load_dotenv()
app = Flask(__name__)
TELNYX_API_KEY = os.getenv("TELNYX_API_KEY")
ASSISTANT_ID = os.getenv("ASSISTANT_ID")
AI_MODEL = os.getenv("AI_MODEL", "moonshotai/Kimi-K2.6")
INFERENCE_URL = "https://api.telnyx.com/v2/ai/chat/completions"

bookings = []
available_slots = [
    {"date": "2026-06-20", "time": "10:00 AM", "available": True},
    {"date": "2026-06-20", "time": "2:00 PM", "available": True},
    {"date": "2026-06-21", "time": "9:00 AM", "available": True},
    {"date": "2026-06-21", "time": "11:00 AM", "available": True},
    {"date": "2026-06-21", "time": "3:00 PM", "available": True},
]

TOOLS = [
    {"type": "function", "function": {"name": "check_availability", "description": "Check available appointment slots", "parameters": {"type": "object", "properties": {"date": {"type": "string", "description": "Date to check (YYYY-MM-DD)"}}, "required": []}}},
    {"type": "function", "function": {"name": "book_appointment", "description": "Book an appointment slot", "parameters": {"type": "object", "properties": {"date": {"type": "string"}, "time": {"type": "string"}, "name": {"type": "string"}, "phone": {"type": "string"}, "reason": {"type": "string"}}, "required": ["date", "time", "name"]}}},
    {"type": "function", "function": {"name": "cancel_appointment", "description": "Cancel an existing appointment", "parameters": {"type": "object", "properties": {"booking_id": {"type": "string"}}, "required": ["booking_id"]}}},
]

def execute_tool(name, args):
    if name == "check_availability":
        date_filter = args.get("date")
        slots = [s for s in available_slots if s["available"] and (not date_filter or s["date"] == date_filter)]
        return json.dumps({"available_slots": slots})
    elif name == "book_appointment":
        for slot in available_slots:
            if slot["date"] == args.get("date") and slot["time"] == args.get("time") and slot["available"]:
                slot["available"] = False
                booking = {"id": f"BK-{int(time.time())}", "date": slot["date"], "time": slot["time"],
                    "name": args.get("name"), "phone": args.get("phone", ""), "reason": args.get("reason", "")}
                bookings.append(booking)
                return json.dumps({"success": True, "booking": booking})
        return json.dumps({"success": False, "error": "Slot not available"})
    elif name == "cancel_appointment":
        bid = args.get("booking_id")
        for b in bookings:
            if b["id"] == bid:
                bookings.remove(b)
                for s in available_slots:
                    if s["date"] == b["date"] and s["time"] == b["time"]:
                        s["available"] = True
                return json.dumps({"success": True, "cancelled": bid})
        return json.dumps({"success": False, "error": "Booking not found"})
    return json.dumps({"error": "Unknown tool"})

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    if not data:
        return jsonify({"error": "invalid request body"}), 400
    messages = data.get("messages", [])
    if not any(m["role"] == "system" for m in messages):
        messages.insert(0, {"role": "system", "content": "You are a friendly office receptionist with access to a real booking system. Use the tools to check availability and book appointments. Be helpful and concise."})
    payload = {"model": AI_MODEL, "messages": messages, "tools": TOOLS, "max_tokens": 300, "temperature": 0.5}
    try:
        resp = requests.post(INFERENCE_URL, headers={"Authorization": f"Bearer {TELNYX_API_KEY}", "Content-Type": "application/json"}, json=payload, timeout=20)
    except Exception as e:
        app.logger.error("Request failed: %s", e)
    resp.raise_for_status()
    choice = resp.json()["choices"][0]
    msg = choice["message"]
    if msg.get("tool_calls"):
        messages.append(msg)
        for tc in msg["tool_calls"]:
            result = execute_tool(tc["function"]["name"], json.loads(tc["function"].get("arguments", "{}")))
            messages.append({"role": "tool", "tool_call_id": tc["id"], "content": result})
        payload["messages"] = messages
        del payload["tools"]
        try:
            resp2 = requests.post(INFERENCE_URL, headers={"Authorization": f"Bearer {TELNYX_API_KEY}", "Content-Type": "application/json"}, json=payload, timeout=20)
        except Exception as e:
            app.logger.error("Request failed: %s", e)
        resp2.raise_for_status()
        msg = resp2.json()["choices"][0]["message"]
    return jsonify({"response": msg["content"], "bookings": len(bookings)}), 200

@app.route("/bookings", methods=["GET"])
def list_bookings():
    return jsonify({"bookings": bookings}), 200

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "bookings": len(bookings), "available_slots": sum(1 for s in available_slots if s["available"])}), 200

if __name__ == "__main__":
    app.run(debug=False, host=os.getenv("HOST", "127.0.0.1"), port=int(os.getenv("PORT", "5000")))
