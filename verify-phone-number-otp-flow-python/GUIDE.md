# Phone Number OTP Verification with Telnyx

Verify Phone Number OTP Flow — Telnyx Verify API with SMS primary and voice call fallback.

## How It Works

```
  User requests verification
        │
        ▼
  ┌──────────────────┐
  │ Generate OTP     │
  └────────┬─────────┘
           │
           ├──► SMS code
           │
           ▼
  ┌──────────────────┐
  │ Verify code      │ ── user submits OTP
  └────────┬─────────┘
           │
           ▼
     ✓ Verified / ✗ Denied
```

## Telnyx Products Used

- **Migration**
- **Number Porting** — phone number search, purchase, and configuration
- **Verify** — phone verification with OTP delivery across channels

## API Endpoints

- **Create Verification**: `POST /v2/verifications` — [API reference](https://developers.telnyx.com/api/verify/create-verification)

## Prerequisites

- Python 3.8+
- [Telnyx account](https://portal.telnyx.com/sign-up) with funded balance
- [API key](https://portal.telnyx.com/api-keys)
- [Phone number](https://portal.telnyx.com/numbers/my-numbers) with voice enabled
- [Call Control Application](https://portal.telnyx.com/call-control/applications) configured with your webhook URL
- [ngrok](https://ngrok.com) for exposing your local server to Telnyx webhooks

## Step 1: Set Up the Project

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/verify-phone-number-otp-flow-python
cp .env.example .env
pip install -r requirements.txt
```

Edit `.env` with your Telnyx credentials. Each variable links to where you find it in the [Telnyx Portal](https://portal.telnyx.com).

## Step 2: Understand the Code

Everything lives in `app.py` (60 lines). Here's what each piece does.

### Starting the Workflow

**`start_verification()`** — Kicks off the main workflow. Validates the request, creates the record, and initiates the Telnyx API calls.

```python
data = request.get_json()
    phone = data.get("phone_number")
    if not phone:
        return jsonify({"error": "phone_number required"}), 400
    try:
        resp = requests.post("https://api.telnyx.com/v2/verifications", headers={"Authorization": f"Bearer {TELNYX_API_KEY}", "Content-Type": "application/json"},
            json={"phone_number": phone, "verify_profile_id": VERIFY_PROFILE_ID, "type": "sms"}, timeout=10)
        if resp.ok:
```

### Business Logic

- **`voice_fallback()`** — Makes an API call and processes the response.
- **`check_verification()`** — Makes an API call and processes the response.

### All Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| `POST` | `/verify/start` | Start Verification |
| `POST` | `/verify/voice-fallback` | Voice Fallback |
| `POST` | `/verify/check` | Check Verification |
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
curl -X POST http://localhost:5000/verify/start \
  -H "Content-Type: application/json" \
  -d '{
    "phone_numbers": ["+12125551234"],
    "carrier": "Current Carrier"
  }'
```

Or call your Telnyx number from any phone to trigger the full voice workflow.

## Going to Production

This example uses in-memory storage for simplicity. For production:

- **Database** — replace the in-memory dict/list with PostgreSQL or Redis
- **Authentication** — add API key validation on your endpoints
- **Webhook verification** — validate Telnyx webhook signatures ([docs](https://developers.telnyx.com/docs/api/v2/overview#webhook-signing))
- **Error recovery** — handle call failures gracefully with retry or SMS fallback
- **Monitoring** — add structured logging and health check alerts
- **Rate limiting** — protect your endpoints from abuse

## Run

```bash
pip install -r requirements.txt
python app.py
```

## Resources

- [Source code and reference](./README.md)
- [Telnyx Developer Docs](https://developers.telnyx.com)
- [Call Control quickstart](https://developers.telnyx.com/docs/voice/call-control)
- [Telnyx Portal](https://portal.telnyx.com)
