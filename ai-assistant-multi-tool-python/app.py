#!/usr/bin/env python3
"""AI Assistant Multi-Tool — AI Assistant with custom function-calling tools for CRM lookup, appointment booking, and order status."""
import os, json, time, requests
from dotenv import load_dotenv
from flask import Flask, request, jsonify
load_dotenv()
app = Flask(__name__)
TELNYX_API_KEY = os.getenv("TELNYX_API_KEY")
AI_MODEL = os.getenv("AI_MODEL", "moonshotai/Kimi-K2.6")
API = "https://api.telnyx.com/v2"
INFERENCE_URL = f"{API}/ai/chat/completions"
headers = {"Authorization": f"Bearer {TELNYX_API_KEY}", "Content-Type": "application/json"}
tool_calls_log = []

MOCK_CRM = {"CUST-001": {"name": "Acme Corp", "plan": "Enterprise", "mrr": 5000, "health": "green"},
    "CUST-002": {"name": "Beta LLC", "plan": "Growth", "mrr": 1200, "health": "yellow"},
    "CUST-003": {"name": "Gamma Inc", "plan": "Starter", "mrr": 300, "health": "red"}}
MOCK_ORDERS = {"ORD-1001": {"customer": "Acme Corp", "status": "shipped", "eta": "2026-06-20"},
    "ORD-1002": {"customer": "Beta LLC", "status": "processing", "eta": "2026-06-25"}}
MOCK_SLOTS = ["2026-06-19 10:00", "2026-06-19 14:00", "2026-06-20 09:00", "2026-06-20 15:00"]

TOOLS = [
    {"type": "function", "function": {"name": "lookup_customer", "description": "Look up customer info by ID",
        "parameters": {"type": "object", "properties": {"customer_id": {"type": "string"}}, "required": ["customer_id"]}}},
    {"type": "function", "function": {"name": "check_order_status", "description": "Check order status by order ID",
        "parameters": {"type": "object", "properties": {"order_id": {"type": "string"}}, "required": ["order_id"]}}},
    {"type": "function", "function": {"name": "book_appointment", "description": "Book an appointment slot",
        "parameters": {"type": "object", "properties": {"customer_id": {"type": "string"}, "slot": {"type": "string"}, "reason": {"type": "string"}}, "required": ["customer_id", "slot"]}}},
    {"type": "function", "function": {"name": "list_available_slots", "description": "List available appointment slots",
        "parameters": {"type": "object", "properties": {}}}},
]

def execute_tool(name, args):
    if name == "lookup_customer":
        return MOCK_CRM.get(args.get("customer_id"), {"error": "Customer not found"})
    elif name == "check_order_status":
        return MOCK_ORDERS.get(args.get("order_id"), {"error": "Order not found"})
    elif name == "list_available_slots":
        return {"slots": MOCK_SLOTS}
    elif name == "book_appointment":
        slot = args.get("slot")
        if slot in MOCK_SLOTS:
            MOCK_SLOTS.remove(slot)
            return {"status": "booked", "slot": slot, "customer": args.get("customer_id")}
        return {"error": "Slot not available"}
    return {"error": "Unknown tool"}

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    if not data:
        return jsonify({"error": "invalid request body"}), 400
    messages = data.get("messages", [])
    if not messages:
        return jsonify({"error": "messages required"}), 400
    system = [{"role": "system", "content": "You are a helpful business assistant with access to CRM, order tracking, and appointment booking tools. Use tools when the user asks about customers, orders, or scheduling."}]
    try:
        resp = requests.post(INFERENCE_URL, headers=headers,
            json={"model": AI_MODEL, "messages": system + messages, "tools": TOOLS,
                "max_tokens": 400, "temperature": 0.3}, timeout=20)
        result = resp.json()
        choice = result.get("choices", [{}])[0]
        message = choice.get("message", {})
        if message.get("tool_calls"):
            for tc in message["tool_calls"]:
                fn = tc.get("function", {})
                tool_result = execute_tool(fn.get("name"), json.loads(fn.get("arguments", "{}")))
                tool_calls_log.append({"tool": fn.get("name"), "args": fn.get("arguments"),
                    "result": tool_result, "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")})
                messages.append(message)
                messages.append({"role": "tool", "tool_call_id": tc.get("id"), "content": json.dumps(tool_result)})
            final = requests.post(INFERENCE_URL, headers=headers,
                json={"model": AI_MODEL, "messages": system + messages, "max_tokens": 400}, timeout=20)
            return jsonify(final.json()), 200
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/tools", methods=["GET"])
def list_tools():
    return jsonify({"tools": TOOLS}), 200

@app.route("/tool-calls", methods=["GET"])
def list_tool_calls():
    return jsonify({"calls": tool_calls_log[-20:]}), 200

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "tools": len(TOOLS), "calls": len(tool_calls_log)}), 200

if __name__ == "__main__":
    app.run(debug=False, host=os.getenv("HOST", "127.0.0.1"), port=int(os.getenv("PORT", "5000")))
