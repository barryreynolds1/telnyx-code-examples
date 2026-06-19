# Set Up a SIP Trunk with Telnyx

Provision and configure a SIP trunk connection on Telnyx with codec preferences, authentication, and failover.

## How It Works

```
  Your PBX / SBC
        │
        ▼
  ┌──────────────────┐
  │ Telnyx SIP Trunk  │
  │ (IP / FQDN auth)  │
  └────────┬─────────┘
           │
           ▼
     PSTN / Telnyx Network
```

## Telnyx Products Used

- **SIP Trunking** — SIP trunking with codec and routing configuration

## API Endpoints

- **Create SIP Connection**: `POST /v2/sip_connections` -- [API reference](https://developers.telnyx.com/api/sip/create-sip-connection)
- **List SIP Connections**: `GET /v2/sip_connections` -- [API reference](https://developers.telnyx.com/api/sip/list-sip-connections)

## Prerequisites

- Python 3.8+
- [Telnyx account](https://portal.telnyx.com/sign-up) with funded balance
- [API key](https://portal.telnyx.com/api-keys)

## Step 1: Set Up the Project

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/setup-sip-trunk-python
cp .env.example .env
pip install -r requirements.txt
```

Edit `.env` with your Telnyx credentials. Each variable links to where you find it in the [Telnyx Portal](https://portal.telnyx.com).

## Step 2: Understand the Code

Everything lives in `app.py` (70 lines). Here's what each piece does.

### Business Logic

- **`setup_sip_endpoint()`** — Processes setup sip endpoint request and returns result.

### All Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| `POST` | `/sip/setup` | Setup Sip Endpoint |

The trigger endpoint kicks off the workflow:

```python
def setup_sip_endpoint():
    """HTTP endpoint to set up SIP trunking."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "invalid request body"}), 400
    
    if not data:
        return jsonify({"error": "Request body required"}), 400
    
    name = data.get("name")
    username = data.get("username")
    password = data.get("password")
```

Helper function that handles the core action:

```python
def create_sip_connection(name: str, username: str, password: str) -> dict:
    """Create SIP connection via Telnyx and return JSON-serializable response data."""
    # Validate input to prevent API errors
    if not name or not username or not password:
        raise ValueError("Name, username, and password are required")
    
    # Use client.sip_connections.create() — NOT client.sip_connections.create()
    response = client.sip_connections.create(
        name=name,
        username=username,
        password=password,
    )
    
    # Extract serializable data — SDK objects are NOT JSON-serializable
```

## Step 3: Run It

```bash
python app.py
```

Server starts on `http://localhost:5000`.

## Step 4: Test It

**Health check:**

```bash
curl http://localhost:5000/health
```

**Trigger the workflow:**

```bash
curl -X POST http://localhost:5000/sip/setup \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Production SIP Trunk",
    "domain": "sip.example.com"
  }'
```

## Going to Production

This example uses in-memory storage for simplicity. For production:

- **Database** — replace the in-memory dict/list with PostgreSQL or Redis
- **Authentication** — add API key validation on your endpoints
- **Webhook verification** — validate Telnyx webhook signatures ([docs](https://developers.telnyx.com/docs/api/v2/overview#webhook-signing))
- **Monitoring** — add structured logging and health check alerts
- **Rate limiting** — protect your endpoints from abuse

## Deploy

```bash
# Docker
docker build -t setup-sip-trunk-python .
docker run --env-file .env -p 5000:5000 setup-sip-trunk-python

# Or Makefile
make setup && make run
```

## Resources

- [Source code and reference](./README.md)
- [Telnyx Developer Docs](https://developers.telnyx.com)
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

