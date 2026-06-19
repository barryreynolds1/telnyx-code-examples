# How to Connect SIP Trunking to a Voice AI Agent

Connect your existing PBX or SBC to Telnyx SIP trunking, then route calls to an AI voice agent. Keep your current phone system while adding AI capabilities.

## Architecture

```
Your PBX / SBC
      |
      | SIP (TLS/UDP)
      v
Telnyx SIP Trunk
      |
      | Inbound routing rules
      v
Call Control Application
      |
      | Webhooks
      v
Your AI Agent (Flask app)
      |
      | Telnyx Inference API
      v
AI Response -> TTS -> Caller hears it
```

## What this gives you

- **Keep your PBX**: Asterisk, FreeSWITCH, 3CX, Cisco, Avaya all work
- **Elastic capacity**: No fixed channel limits. Scale to thousands of concurrent calls
- **AI on any call**: Route specific DID ranges or IVR menu options to your AI agent
- **Failover**: Automatic failover between SIP endpoints if one goes down
- **One network**: SIP trunking and AI inference on the same Telnyx backbone

## Prerequisites

- [Telnyx account](https://portal.telnyx.com/sign-up) with API key
- Python 3.8+
- A PBX or SBC that supports SIP trunking (or use Telnyx Call Control directly)
- [ngrok](https://ngrok.com) for webhook development

## Step 1: Provision the SIP trunk

```python
import telnyx

telnyx.api_key = "KEY01234..."

# Create a SIP connection
connection = telnyx.SipConnection.create(
    connection_name="ai-voice-trunk",
    transport_protocol="TLS",
    authentication={
        "type": "credentials",
        "username": "your-sip-user",
        "password": "your-sip-password",
    },
    outbound={
        "outbound_voice_profile_id": "your-ovp-id",
    },
)
print(f"SIP Connection ID: {connection.id}")
print(f"SIP URI: sip:{connection.sip_uri}")
```

Or use the [Telnyx Portal](https://portal.telnyx.com/sip-trunking) to create it visually.

## Step 2: Configure your PBX to point at Telnyx

Point your PBX outbound trunk to the Telnyx SIP URI. For Asterisk:

```ini
; /etc/asterisk/pjsip.conf
[telnyx-trunk]
type=endpoint
transport=transport-tls
context=from-telnyx
disallow=all
allow=opus,g722,ulaw
outbound_auth=telnyx-auth
aors=telnyx-aor

[telnyx-auth]
type=auth
auth_type=userpass
username=your-sip-user
password=your-sip-password

[telnyx-aor]
type=aor
contact=sip:sip.telnyx.com:5061\;transport=tls
```

## Step 3: Route inbound calls to your AI agent

Create a Call Control Application in the [Telnyx Portal](https://portal.telnyx.com/call-control/applications) with your webhook URL, then assign phone numbers to it.

Or route programmatically:

```python
@app.route("/webhooks/voice", methods=["POST"])
def handle_voice():
    event = request.get_json()["data"]

    if event["event_type"] == "call.initiated":
        call_id = event["payload"]["call_control_id"]
        dialed_number = event["payload"].get("to", "")

        # Route AI-enabled numbers to the AI handler
        if dialed_number in AI_ENABLED_NUMBERS:
            requests.post(
                f"https://api.telnyx.com/v2/calls/{call_id}/actions/answer",
                headers={"Authorization": f"Bearer {API_KEY}"},
                json={},
            )
        else:
            # Forward to PBX for human handling
            requests.post(
                f"https://api.telnyx.com/v2/calls/{call_id}/actions/transfer",
                headers={"Authorization": f"Bearer {API_KEY}"},
                json={"to": "+15551234567"},  # your PBX DID
            )
```

## Step 4: Add AI to the call

Once the call is answered, use the same STT -> Inference -> TTS loop from the [voice AI agent guide](./route-phone-call-to-ai-agent-python.md).

## Failover configuration

```python
# Configure failover so calls route to backup if primary is down
connection = telnyx.SipConnection.update(
    connection_id,
    inbound={
        "failover_enabled": True,
        "failover_sip_uri": "sip:backup-pbx.yourcompany.com",
    },
)
```

## Why Telnyx SIP trunking for AI?

- **Co-located**: SIP termination and AI inference on the same network. No extra latency from routing calls to a separate AI vendor.
- **Elastic**: No channel limits. Pay per minute, not per trunk.
- **BYOC**: Bring your own carrier model if you need to keep existing numbers during migration.
- **Global**: Local numbers and SIP termination in 60+ countries.

## Full source code

- [setup-sip-trunk-python](https://github.com/team-telnyx/telnyx-code-examples/tree/main/setup-sip-trunk-python)
- [inbound-sip-routing-python](https://github.com/team-telnyx/telnyx-code-examples/tree/main/inbound-sip-routing-python)
- [sip-failover-routing-python](https://github.com/team-telnyx/telnyx-code-examples/tree/main/sip-failover-routing-python)

## Resources

- [Telnyx SIP Trunking docs](https://developers.telnyx.com/docs/voice/sip-trunking)
- [Call Control docs](https://developers.telnyx.com/docs/voice/call-control)
- [Telnyx Portal](https://portal.telnyx.com)
