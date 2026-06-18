#!/usr/bin/env python3
"""Edge Compute Webhook Proxy — deploy a webhook handler to Telnyx edge for low-latency event processing and routing."""
import os, json, time, requests, subprocess
from dotenv import load_dotenv
from flask import Flask, request, jsonify
load_dotenv()
app = Flask(__name__)
TELNYX_API_KEY = os.getenv("TELNYX_API_KEY")
EDGE_API = "https://api.telnyx.com/v2"
headers = {"Authorization": f"Bearer {TELNYX_API_KEY}", "Content-Type": "application/json"}
deployed_functions = []
event_log = []

WEBHOOK_HANDLER_CODE = """
export default {
  async fetch(request, env) {
    const payload = await request.json();
    const eventType = payload?.data?.event_type || 'unknown';
    const timestamp = new Date().toISOString();

    // Route events to downstream services
    const routes = {
      'call.initiated': env.VOICE_HANDLER_URL,
      'call.answered': env.VOICE_HANDLER_URL,
      'call.hangup': env.VOICE_HANDLER_URL,
      'message.received': env.MESSAGE_HANDLER_URL,
      'message.sent': env.MESSAGE_HANDLER_URL,
    };

    const targetUrl = routes[eventType] || env.DEFAULT_HANDLER_URL;
    if (targetUrl) {
      await fetch(targetUrl, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({...payload, _edge_processed: true, _edge_timestamp: timestamp})
      });
    }

    return new Response(JSON.stringify({status: 'processed', event: eventType, timestamp}),
      {headers: {'Content-Type': 'application/json'}});
  }
};
"""

@app.route("/deploy", methods=["POST"])
def deploy_function():
    data = request.get_json()
    func = {"name": data.get("name", f"webhook-proxy-{int(time.time())}"),
        "code": WEBHOOK_HANDLER_CODE,
        "secrets": {"VOICE_HANDLER_URL": data.get("voice_url", ""),
            "MESSAGE_HANDLER_URL": data.get("message_url", ""),
            "DEFAULT_HANDLER_URL": data.get("default_url", "")},
        "status": "deployed", "deployed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ")}
    deployed_functions.append(func)
    return jsonify({"status": "deployed", "function": func["name"],
        "note": "In production, use `telnyx-edge ship` CLI to deploy to edge infrastructure"}), 200

@app.route("/webhook", methods=["POST"])
def handle_webhook():
    payload = request.get_json()
    event_type = payload.get("data", {}).get("event_type", "unknown")
    entry = {"event_type": event_type,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "payload_size": len(json.dumps(payload)),
        "processed": True}
    event_log.append(entry)
    return jsonify({"status": "processed", "event": event_type}), 200

@app.route("/functions", methods=["GET"])
def list_functions():
    return jsonify({"functions": deployed_functions}), 200

@app.route("/events", methods=["GET"])
def list_events():
    return jsonify({"events": event_log[-100:]}), 200

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "functions": len(deployed_functions), "events_processed": len(event_log)}), 200

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
