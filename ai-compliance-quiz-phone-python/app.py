#!/usr/bin/env python3
"""AI Compliance Quiz Phone — employees call in and take a compliance quiz. The AI
asks questions, grades spoken answers, scores pass/fail, and records completion.

Per-call state lives in Telnyx ``client_state`` — a base64-encoded JSON object that
Telnyx echoes back on every webhook for the call. The server keeps no per-call
state, so it survives restarts and scales horizontally with no shared store.
"""
import os, json, base64, time, requests, telnyx
from dotenv import load_dotenv
from flask import Flask, request, jsonify

load_dotenv()
app = Flask(__name__)
# public_key (from the Portal) lets the SDK verify inbound webhook signatures.
client = telnyx.Telnyx(
    api_key=os.getenv("TELNYX_API_KEY"),
    public_key=os.getenv("TELNYX_PUBLIC_KEY"),
)
TELNYX_API_KEY = os.getenv("TELNYX_API_KEY")
AI_MODEL = os.getenv("AI_MODEL", "moonshotai/Kimi-K2.6")
QUIZ_NUMBER = os.getenv("QUIZ_NUMBER")
INFERENCE_URL = "https://api.telnyx.com/v2/ai/chat/completions"

# Append-only log of finished quizzes (use a database in production).
completions = []

QUIZ_QUESTIONS = [
    {"q": "Is it ever acceptable to share your login credentials with a coworker who needs urgent access?", "correct": "No — credentials should never be shared. The coworker should request their own access through IT."},
    {"q": "You receive an email from the CEO asking you to wire transfer $50,000 immediately. The email address looks slightly different. What do you do?", "correct": "Do not comply. Verify through a separate channel like phone call to the CEO's known number. This is likely a BEC (business email compromise) attack."},
    {"q": "A customer asks you to look up another customer's account information. They claim to be their spouse. What's the right action?", "correct": "Decline. Verify authorization through proper channels. Customer data requires explicit consent from the account holder."},
    {"q": "You find a USB drive in the parking lot. What should you do?", "correct": "Do not plug it into any computer. Turn it in to IT security. It could contain malware."},
    {"q": "Is it okay to discuss company financial results with friends before the public earnings call?", "correct": "No. This is insider information and sharing it violates securities law."},
]


def encode_state(state: dict) -> str:
    """Stringify the state object and base64-encode it — the value Telnyx round-trips."""
    return base64.b64encode(json.dumps(state).encode()).decode()


def decode_state(payload: dict) -> dict:
    """Recover the state object echoed back on the webhook payload."""
    raw = payload.get("client_state")
    if not raw:
        return {}
    try:
        return json.loads(base64.b64decode(raw))
    except Exception:
        return {}


def call_inference(messages, max_tokens=150):
    resp = requests.post(
        INFERENCE_URL,
        headers={"Authorization": f"Bearer {TELNYX_API_KEY}", "Content-Type": "application/json"},
        json={"model": AI_MODEL, "messages": messages, "max_tokens": max_tokens, "temperature": 0.2},
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


@app.route("/webhooks/voice", methods=["POST"])
def handle_voice():
    # Verify the Telnyx Ed25519 signature against the raw body before trusting
    # anything. unwrap() reads the telnyx-signature-ed25519 / telnyx-timestamp
    # headers and raises if the signature or timestamp (replay) check fails.
    try:
        client.webhooks.unwrap(request.get_data(as_text=True), headers=dict(request.headers))
    except Exception:
        return jsonify({"error": "invalid signature"}), 401
    body = request.get_json(silent=True)
    if not body:
        return jsonify({"error": "invalid request body"}), 400

    data = body.get("data", {})
    event_type = data.get("event_type")
    p = data.get("payload", {})            # Telnyx nests event fields under data.payload
    ccid = p.get("call_control_id")
    state = decode_state(p)                # per-call state carried by Telnyx

    if event_type == "call.initiated" and p.get("direction") == "incoming":
        init = {"caller": p.get("from"), "idx": 0, "scores": [], "phase": "greeting"}
        client.calls.actions.answer(ccid, client_state=encode_state(init))
        return jsonify({"status": "answering"}), 200

    if event_type == "call.answered":
        client.calls.actions.speak(
            ccid,
            payload="Welcome to the quarterly compliance quiz. I'll ask 5 questions. Answer each one verbally. Let's begin.",
            voice="female", language_code="en-US",
            client_state=encode_state(state),
        )
        return jsonify({"status": "greeting"}), 200

    if event_type == "call.speak.ended":
        idx = state.get("idx", 0)
        if state.get("phase") in ("greeting", "feedback") and idx < len(QUIZ_QUESTIONS):
            # Just finished the greeting / previous feedback -> ask the current question.
            client.calls.actions.speak(
                ccid,
                payload=f"Question {idx + 1}: {QUIZ_QUESTIONS[idx]['q']}",
                voice="female", language_code="en-US",
                client_state=encode_state({**state, "phase": "question"}),
            )
        elif state.get("phase") == "question":
            # Just finished speaking the question -> gather the spoken answer.
            client.calls.actions.gather(
                ccid, input_type="speech", end_silence_timeout_secs=3,
                timeout_secs=30, language_code="en-US",
                client_state=encode_state({**state, "phase": "answering"}),
            )
        return jsonify({"status": "asking"}), 200

    if event_type == "call.gather.ended":
        idx = state.get("idx", 0)
        speech = (p.get("speech") or {}).get("result", "")
        if idx < len(QUIZ_QUESTIONS):
            if speech:
                q = QUIZ_QUESTIONS[idx]
                grade = call_inference([
                    {"role": "system", "content": f"Grade this compliance quiz answer. Correct answer: {q['correct']}. Return JSON: correct (boolean), score (0-10), feedback (1 sentence)."},
                    {"role": "user", "content": speech},
                ])
                try:
                    result = json.loads(grade)
                except Exception:
                    result = {"correct": False, "score": 5, "feedback": "Answer noted."}
            else:
                result = {"correct": False, "score": 0, "feedback": "No answer detected."}
            scores = state.get("scores", []) + [result.get("score", 0)]
            feedback = result.get("feedback", "")
            nxt = idx + 1
            if nxt < len(QUIZ_QUESTIONS):
                client.calls.actions.speak(
                    ccid, payload=f"{feedback} Next question.",
                    voice="female", language_code="en-US",
                    client_state=encode_state({**state, "idx": nxt, "scores": scores, "phase": "feedback"}),
                )
            else:
                total = sum(scores)
                passed = total >= 35
                client.calls.actions.speak(
                    ccid,
                    payload=f"{feedback}. Quiz complete! Score: {total} out of 50. {'You passed!' if passed else 'Please retake the quiz after reviewing the compliance handbook.'}",
                    voice="female", language_code="en-US",
                    client_state=encode_state({**state, "idx": nxt, "scores": scores, "phase": "done"}),
                )
        return jsonify({"status": "grading"}), 200

    if event_type == "call.hangup":
        scores = state.get("scores", [])
        if scores:
            total = sum(scores)
            completions.append({
                "caller": state.get("caller"), "score": total, "max": 50,
                "passed": total >= 35, "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            })
        return jsonify({"status": "ended"}), 200

    return jsonify({"status": "ok"}), 200


@app.route("/completions", methods=["GET"])
def list_completions():
    return jsonify({"completions": completions[-50:]}), 200


@app.route("/health", methods=["GET"])
def health():
    passed = sum(1 for c in completions if c.get("passed"))
    return jsonify({"status": "ok", "total": len(completions), "passed": passed}), 200


if __name__ == "__main__":
    app.run(debug=False, host=os.getenv("HOST", "127.0.0.1"), port=int(os.getenv("PORT", "5000")))
