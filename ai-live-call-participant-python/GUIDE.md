# Build an AI Live Call Participant

AI joins a live multi-human conference call as an active participant. Listens via media streaming, contributes via TTS, takes notes, responds when addressed by name.

## How It Works

```
  Participants
    │   │   │
    ▼   ▼   ▼
  ┌──────────────────────────┐
  │  Telnyx Conference Bridge  │
  │  (mixed audio stream)      │
  └────────────┬───────────────┘
               │ media stream
               ▼
  ┌──────────────────────────┐
  │  AI Inference             │
  │  • Escalation logic       │
  │  • Summarization          │
  └────────────┬───────────────┘
               │
               ├──► Voice response
               └──► Slack alert

  State: In-memory dict
```

## Telnyx Products Used

- **Voice** — programmatic call control with webhooks for every call state change
- **AI Inference** — LLM inference with OpenAI-compatible API, runs on Telnyx infrastructure
- **Media Streaming**
- **Conferencing**

## API Endpoints

- **AI Inference**: `POST /v2/ai/chat/completions` — [API reference](https://developers.telnyx.com/api/inference/chat-completions)

## Webhook Events

Telnyx uses webhooks for call control — you don't poll for state. Each event tells you what happened, and your response tells Telnyx what to do next.

This app handles these webhook events ([Call Control docs](https://developers.telnyx.com/docs/api/v2/call-control)):
- `call.answered` — Call connected — app begins interaction
- `call.gather.ended` — Caller input received (speech transcription or DTMF digits)
- `call.hangup` — Call ended — app cleans up session, triggers post-call processing
- `call.initiated` — New inbound or outbound call detected
- `call.speak.ended` — TTS playback finished — app transitions to next action (gather, transfer, etc.)

## Prerequisites

- Python 3.8+
- [Telnyx account](https://portal.telnyx.com/sign-up) with funded balance
- [API key](https://portal.telnyx.com/api-keys)
- [Phone number](https://portal.telnyx.com/numbers/my-numbers) with voice enabled
- [Call Control Application](https://portal.telnyx.com/call-control/applications) configured with your webhook URL
- [Slack incoming webhook](https://api.slack.com/messaging/webhooks) (optional)
- [ngrok](https://ngrok.com) for exposing your local server to Telnyx webhooks

## Step 1: Set Up the Project

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/ai-live-call-participant-python
cp .env.example .env
pip install -r requirements.txt
```

Edit `.env` with your Telnyx credentials. Each variable links to where you find it in the [Telnyx Portal](https://portal.telnyx.com).

## Step 2: Understand the Code

Everything lives in `app.py` (268 lines). Here's what each piece does.

### Starting the Workflow

**`create_conference()`** — Kicks off the main workflow. Validates the request, creates the record, and initiates the Telnyx API calls.

```python
    data = request.get_json() or {}
    conf_name = data.get("name", f"ai-conf-{int(time.time())}")
    participants = data.get("participants", [])
    conf = {
        "name": conf_name,
        "created_at": time.time(),
        "participants": {},
        "transcript": [],
```

### Handling Webhooks

This is the core of the app — a state machine driven by Telnyx webhook events. Each event triggers the next step:

**`handle_voice()`** — The voice webhook handler — the core state machine. Each Telnyx event triggers the next action in the call flow.

- `call.initiated` → call setup in progress
- `call.answered` → greet the caller with TTS
- `call.speak.ended` → start gathering input
- `call.gather.ended` → process the caller's response

### Helper Functions

- **`call_inference()`** — Sends conversation context to Telnyx AI Inference and returns the model's response. Uses the OpenAI-compatible chat completions endpoint.

### Business Logic

- **`telnyx_post()`** — Makes an API call and processes the response.
- **`post_slack()`** — Makes an API call and processes the response.
- **`handle_media()`** — Processes inbound media event.

### All Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| `POST` | `/conferences/create` | Create Conference |
| `POST` | `/webhooks/voice` | Telnyx webhook handler |
| `POST` | `/webhooks/media` | Telnyx webhook handler |
| `GET` | `/conferences` | List Conferences |
| `GET` | `/conferences/<name>/transcript` | Get Transcript |
| `POST` | `/conferences/<name>/ask` | Ask Ai |
| `GET` | `/health` | Health check |

## Step 3: Run It

```bash
python app.py
```

Server starts on `http://localhost:5000`.

In a separate terminal, expose your server for webhooks:

```bash
ngrok http 5000
```

Copy the HTTPS URL and set it in the [Telnyx Portal](https://portal.telnyx.com):

- **Call Control Application** → Webhook URL → `https://<id>.ngrok.io/webhooks/voice`

## Step 4: Test It

**Health check:**

```bash
curl http://localhost:5000/health
```

**Trigger the workflow:**

```bash
curl -X POST http://localhost:5000/conferences/create \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+12125559999"
  }'
```

Or call your Telnyx number from any phone to trigger the full voice workflow.

**Check results:**

```bash
curl http://localhost:5000/conferences | python3 -m json.tool
```

## Going to Production

This example uses in-memory storage for simplicity. For production:

- **Database** — replace the in-memory dict/list with PostgreSQL or Redis
- **Authentication** — add API key validation on your endpoints
- **Webhook verification** — validate Telnyx webhook signatures ([docs](https://developers.telnyx.com/docs/api/v2/overview#webhook-signing))
- **Error recovery** — handle call failures gracefully with retry or SMS fallback
- **Prompt engineering** — tune the AI prompts for your specific domain and tone
- **Monitoring** — add structured logging and health check alerts
- **Rate limiting** — protect your endpoints from abuse

## Deploy

```bash
# Docker
docker build -t ai-live-call-participant-python .
docker run --env-file .env -p 5000:5000 ai-live-call-participant-python

# Or Makefile
make setup && make run
```

## Resources

- [Source code and reference](./README.md)
- [Telnyx Developer Docs](https://developers.telnyx.com)
- [Call Control quickstart](https://developers.telnyx.com/docs/voice/call-control)
- [AI Inference docs](https://developers.telnyx.com/docs/inference)
- [Telnyx Portal](https://portal.telnyx.com)


## Production Checklist

Before deploying to production, verify each item:

### Authentication and Security
- [ ] API key stored in environment variable or secrets manager, never in code
- [ ] `TELNYX_PUBLIC_KEY` set for webhook signature verification
- [ ] HTTPS endpoint for all webhooks (Telnyx rejects HTTP in production)
- [ ] Input validation on all webhook payloads
- [ ] Rate limiting on public-facing API endpoints

### Webhook Reliability
- [ ] Webhook endpoint returns 200 within 5 seconds (Telnyx retries on timeout)
- [ ] Idempotent webhook handling (same event delivered twice produces same result)
- [ ] Webhook failover URL configured in Telnyx Portal
- [ ] Dead letter queue or logging for failed webhook processing

### Error Handling and Retries
- [ ] `timeout=` set on all outbound HTTP requests (recommended: 10-15s)
- [ ] Retry logic with exponential backoff for Telnyx API calls
- [ ] Graceful fallback when AI inference is slow or unavailable (e.g., transfer to human)
- [ ] Circuit breaker for external service dependencies (Slack, CRM, etc.)

### Latency
- [ ] AI model selected for latency profile (smaller models for real-time voice)
- [ ] System prompts optimized for short responses (1-2 sentences for phone)
- [ ] Streaming TTS enabled where supported
- [ ] Latency measured and logged per call (`inference_ms`, `tts_ms`)

### Observability
- [ ] Structured logging with call IDs for correlation
- [ ] Health check endpoint (`/health`) returning service status
- [ ] Alerting on webhook processing errors
- [ ] Call duration and AI response time metrics exported

### Compliance
- [ ] Call recording disclosure (if recording is enabled)
- [ ] GDPR/CCPA data handling for call transcripts and AI logs
- [ ] PCI compliance if handling payment information by voice
- [ ] HIPAA compliance if handling healthcare data (BAA with Telnyx)

### Deployment
- [ ] Application runs behind a reverse proxy (nginx, Caddy) in production
- [ ] Process manager (systemd, PM2, Docker) for auto-restart
- [ ] Environment-specific configuration (dev/staging/prod API keys)
- [ ] Database or Redis for session state (not in-memory dicts for multi-process)
- [ ] Horizontal scaling plan (sticky sessions or shared state for active calls)

