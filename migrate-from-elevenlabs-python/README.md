# Migrate from ElevenLabs — import ElevenLabs voice configurations to Telnyx TTS with voice mapping and cost comparison.

Migrate from ElevenLabs — import ElevenLabs voice configurations to Telnyx TTS with voice mapping and cost comparison.

## How It Works

```
Inbound Call ──► Telnyx ──► POST /webhooks/voice
                                    │
                               call.initiated → answer
                               call.answered  → speak greeting
                               call.speak.ended → gather (listen)
                               call.gather.ended → process → speak response
                               call.hangup → cleanup
```

## Environment Variables

| Variable | Type | Format | Required | Description |
|----------|------|--------|----------|-------------|
| `TELNYX_API_KEY` | string | `KEY...` | **yes** | Telnyx API v2 key ([get it](https://portal.telnyx.com/api-keys)) |
| `ELEVENLABS_API_KEY` | string | `token` | **yes** | elevenlabs api key |

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

### Docker

```bash
docker build -t migrate-from-elevenlabs .
docker run --env-file .env -p 5000:5000 migrate-from-elevenlabs
```

## API Reference

### `GET /audit/elevenlabs`

```bash
curl http://localhost:5000/audit/elevenlabs
```

### `POST /migrate/voice-config`

```bash
curl -X POST http://localhost:5000/migrate/voice-config \
  -H "Content-Type: application/json" \
  -d '{
  "elevenlabs_voice_name": "Jane Doe",
  "speed": "1.0"
}'
```

### `GET /mapping/voices`

```bash
curl http://localhost:5000/mapping/voices
```

### `GET /cost-comparison`

```bash
curl http://localhost:5000/cost-comparison
```

### `POST /test-tts`

```bash
curl -X POST http://localhost:5000/test-tts \
  -H "Content-Type: application/json" \
  -d '{
  "text": "Hello, this is a test of Telnyx text to speech.",
  "voice_id": "en-US-Neural2-F"
}'
```

### `GET /migration-log`

```bash
curl http://localhost:5000/migration-log
```

### `GET /health`

Health check and service status.

```bash
curl http://localhost:5000/health
```

```json
{"status": "ok"}
```

## Resources

- [Telnyx Developer Docs](https://developers.telnyx.com)
- [Telnyx Portal](https://portal.telnyx.com)
- [API Reference](https://developers.telnyx.com/api)
