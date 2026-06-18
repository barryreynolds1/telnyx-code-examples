# Post-Service Follow-Up Engine

After appointment, SMS satisfaction survey. Negative responses trigger AI voice callback to understand the issue, then creates ticket in Jira and alerts manager via Slack.

## Telnyx APIs

| API | Endpoint | Docs |
|-----|----------|------|
| Call Control: Speak | `POST /v2/calls/{id}/actions/speak` | [docs](https://developers.telnyx.com/docs/voice/call-control) |
| Call Control: Gather | `POST /v2/calls/{id}/actions/gather` | [docs](https://developers.telnyx.com/docs/voice/call-control) |
| AI Inference API | `POST /v2/ai/chat/completions` | [docs](https://developers.telnyx.com/docs/inference) |

## Webhook Events Handled

```
call.answered
call.speak.ended
call.gather.ended
call.hangup
call.gather.ended (speech)
```

## External Integrations

| Service | APIs Used |
|---------|-----------|
| Jira | Issue Create, REST API v3 |
| HubSpot | Contacts Search, CRM API |
| Slack | Incoming Webhooks |

## How It Works

```
Inbound Call/SMS ──► Telnyx ──► POST /webhooks/voice or /webhooks/sms
                                        │
                                        ├── Telnyx AI Inference
                                        ├── Jira
                                        ├── HubSpot
                                        ├── Slack
                                        │
                                        ▼
                                  Response / Action
                                  (speak, SMS, dispatch)
```

## Environment Variables

| Variable | Type | Format | Required | Description |
|----------|------|--------|----------|-------------|
| `TELNYX_API_KEY` | string | `KEY...` | **yes** | Telnyx API v2 key ([get it](https://portal.telnyx.com/api-keys)) |
| `MAIN_NUMBER` | string | `+E.164` | **yes** | Telnyx phone number ([get it](https://portal.telnyx.com/numbers)) |
| `CONNECTION_ID` | string | `uuid` | **yes** | Call Control connection ID ([get it](https://portal.telnyx.com/call-control/applications)) |
| `AI_MODEL` | string | `provider/model` | no | Telnyx inference model ([get it](https://developers.telnyx.com/docs/inference)) |
| `JIRA_URL` | string | `https://co.atlassian.net` | no | Jira instance base URL ([get it](Jira admin)) |
| `JIRA_EMAIL` | string | `email` | no | Jira account email ([get it](Jira account)) |
| `JIRA_TOKEN` | string | `token` | no | Jira API token ([get it](https://id.atlassian.com/manage/api-tokens)) |
| `JIRA_PROJECT` | string | `KEY` | no | Jira project key ([get it](Jira project settings)) |
| `MANAGER_SLACK_WEBHOOK` | string | `https://hooks.slack.com/services/...` | no | Slack webhook for manager alerts ([get it](https://api.slack.com/messaging/webhooks)) |
| `HUBSPOT_API_KEY` | string | `pat-...` | no | HubSpot private app token ([get it](HubSpot > Settings > Private Apps)) |

## Setup

```bash
cp .env.example .env
pip install -r requirements.txt
python app.py
# Server starts on http://localhost:5000
```

### Webhook URL

Expose with [ngrok](https://ngrok.com): `ngrok http 5000`

Configure in [Telnyx Portal](https://portal.telnyx.com):

- **Call Control App** → Webhook URL: `https://<ngrok>.ngrok.io/webhooks/voice`
- **Messaging Profile** → Webhook URL: `https://<ngrok>.ngrok.io/webhooks/sms`

### Docker

```bash
docker build -t post-service-followup-engine .
docker run --env-file .env -p 5000:5000 post-service-followup-engine
```

## API Reference

### `POST /follow-up/send`

Trigger the workflow.

```bash
curl -X POST http://localhost:5000/follow-up/send \
  -H "Content-Type: application/json" \
  -d '{
  "phone": "+12125551234",
  "service": "service",
  "tech": "our technician"
}'
```

### `GET /follow-ups`

Returns all followups.

```bash
curl http://localhost:5000/follow-ups
```

### `GET /health`

Health check and service status.

```bash
curl http://localhost:5000/health
```

```json
{"status": "ok"}
```

## Webhook Endpoints

### `POST /webhooks/sms`

Receives Telnyx Messaging webhook events.

Example payload:

```json
{
  "data": {
    "event_type": "message.received",
    "payload": {
      "from": {
        "phone_number": "+12125551234"
      },
      "to": [
        {
          "phone_number": "+13105559876"
        }
      ],
      "text": "Hello",
      "media": []
    }
  }
}
```

### `POST /webhooks/voice`

Receives Telnyx Call Control webhook events.

Events handled: `call.answered`, `call.speak.ended`, `call.gather.ended`, `call.hangup`, `call.gather.ended (speech)`

Example payload:

```json
{
  "data": {
    "event_type": "call.initiated",
    "call_control_id": "v3:abc-123",
    "direction": "incoming",
    "from": "+12125551234",
    "to": "+13105559876"
  }
}
```

## Resources

- [Call Control: Speak](https://developers.telnyx.com/docs/voice/call-control)
- [AI Inference API](https://developers.telnyx.com/docs/inference)
- [Telnyx Portal](https://portal.telnyx.com)
- [API Reference](https://developers.telnyx.com/api)
