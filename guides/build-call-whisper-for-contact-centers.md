# How to Build Call Whisper for Contact Centers

Call whisper lets a supervisor listen to a live call and coach the agent without the customer hearing. This guide shows how to build whisper, silent monitoring, and barge-in with Telnyx Call Control.

## What is call whisper?

Three monitoring modes for contact centers:

| Mode | Supervisor hears | Agent hears supervisor | Customer hears supervisor |
|------|-----------------|----------------------|--------------------------|
| **Silent monitor** | Yes | No | No |
| **Whisper** | Yes | Yes | No |
| **Barge-in** | Yes | Yes | Yes |

All three use the same Telnyx Conference API with different audio settings per leg.

## How it works

```
Customer <---> Agent       (normal two-way call)
                |
                v
          Conference Bridge
                |
                v
         Supervisor joins
         with audio controls:
         - mute: customer cant hear supervisor
         - unmute: supervisor whispers to agent
         - barge: everyone hears everyone
```

## Prerequisites

- Python 3.8+
- [Telnyx account](https://portal.telnyx.com/sign-up) with API key
- Telnyx phone number with voice enabled
- [Call Control Application](https://portal.telnyx.com/call-control/applications)

## Step 1: Create the conference bridge

When a customer calls, create a conference and add both the customer and agent:

```python
@app.route("/webhooks/voice", methods=["POST"])
def handle_voice():
    event = request.get_json()["data"]
    call_id = event["payload"]["call_control_id"]

    if event["event_type"] == "call.answered":
        conf_name = f"call-{int(time.time())}"

        # Add customer to conference
        requests.post(
            f"https://api.telnyx.com/v2/calls/{call_id}/actions/join_conference",
            headers={"Authorization": f"Bearer {API_KEY}"},
            json={
                "conference_name": conf_name,
                "start_conference_on_enter": True,
                "hold": False,
                "mute": False,
            },
        )

        # Dial the agent and add to same conference
        agent_call = requests.post(
            "https://api.telnyx.com/v2/calls",
            headers={"Authorization": f"Bearer {API_KEY}"},
            json={
                "to": AGENT_NUMBER,
                "from": TELNYX_NUMBER,
                "connection_id": CONNECTION_ID,
            },
        )
        # When agent answers, join them to the conference too
```

## Step 2: Supervisor joins in whisper mode

The supervisor joins the same conference but with `mute=True` and `supervisor_role=True`:

```python
@app.route("/monitor/start", methods=["POST"])
def start_monitoring():
    data = request.get_json()
    conf_name = data["conference"]
    mode = data.get("mode", "silent")  # silent, whisper, or barge

    # Dial the supervisor
    sup_call = requests.post(
        "https://api.telnyx.com/v2/calls",
        headers={"Authorization": f"Bearer {API_KEY}"},
        json={
            "to": SUPERVISOR_NUMBER,
            "from": TELNYX_NUMBER,
            "connection_id": CONNECTION_ID,
        },
    )

    # When supervisor answers, join conference with appropriate settings
    # Silent: muted, cant be heard by anyone
    # Whisper: unmuted, but only agent leg receives audio
    # Barge: unmuted, all legs receive audio
```

## Step 3: Switch modes live

```python
@app.route("/monitor/mode", methods=["POST"])
def change_mode():
    data = request.get_json()
    sup_call_id = data["supervisor_call_id"]
    new_mode = data["mode"]

    if new_mode == "silent":
        # Mute supervisor
        requests.post(
            f"https://api.telnyx.com/v2/calls/{sup_call_id}/actions/mute",
            headers={"Authorization": f"Bearer {API_KEY}"},
            json={},
        )

    elif new_mode == "whisper":
        # Unmute supervisor, but only to agent leg
        requests.post(
            f"https://api.telnyx.com/v2/calls/{sup_call_id}/actions/unmute",
            headers={"Authorization": f"Bearer {API_KEY}"},
            json={},
        )
        # Configure conference to route supervisor audio only to agent

    elif new_mode == "barge":
        # Unmute supervisor to all participants
        requests.post(
            f"https://api.telnyx.com/v2/calls/{sup_call_id}/actions/unmute",
            headers={"Authorization": f"Bearer {API_KEY}"},
            json={},
        )

    return jsonify({"mode": new_mode})
```

## Adding AI to whisper

Combine whisper with AI for automated coaching:

```python
# Instead of a human supervisor, an AI agent monitors the call
# via media streaming and whispers suggestions to the agent

@app.route("/webhooks/voice", methods=["POST"])
def handle_voice():
    event = request.get_json()["data"]

    if event["event_type"] == "call.gather.ended":
        transcript = event["payload"].get("speech", {}).get("result", "")

        # AI analyzes the conversation and generates coaching
        coaching = call_inference(
            f"You are a sales coach. The customer just said: {transcript}. "
            f"Give one sentence of advice for the sales rep."
        )

        # Whisper the coaching to the agent only
        requests.post(
            f"https://api.telnyx.com/v2/calls/{agent_call_id}/actions/speak",
            headers={"Authorization": f"Bearer {API_KEY}"},
            json={"payload": coaching, "language": "en-US"},
        )
```

See [ai-sales-coach-whisper-python](https://github.com/team-telnyx/telnyx-code-examples/tree/main/ai-sales-coach-whisper-python) for the full implementation.

## Full source code

- [call-whisper-monitoring-python](https://github.com/team-telnyx/telnyx-code-examples/tree/main/call-whisper-monitoring-python)
- [ai-sales-coach-whisper-python](https://github.com/team-telnyx/telnyx-code-examples/tree/main/ai-sales-coach-whisper-python)
- [call-whisper-screen-pop-python](https://github.com/team-telnyx/telnyx-code-examples/tree/main/call-whisper-screen-pop-python)

## Resources

- [Telnyx Conference API docs](https://developers.telnyx.com/docs/voice/conferencing)
- [Call Control docs](https://developers.telnyx.com/docs/voice/call-control)
- [Telnyx Portal](https://portal.telnyx.com)
