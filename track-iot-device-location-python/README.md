# Production-ready Flask application for device location tracking via Telnyx IoT API.

Production-ready Flask application for device location tracking via Telnyx IoT API.

## How It Works

```
API Call ──► Your App ──► Telnyx APIs ──► Customer
```

## Environment Variables

| Variable | Type | Format | Required | Description |
|----------|------|--------|----------|-------------|
| `TELNYX_API_KEY` | string | `KEY...` | **yes** | Telnyx API v2 key ([get it](https://portal.telnyx.com/api-keys)) |
| `FLASK_DEBUG` | string | `-` | no | flask debug |

## Setup

```bash
cp .env.example .env
pip install -r requirements.txt
python app.py
# Server starts on http://localhost:5000
```

### Docker

```bash
docker build -t track-iot-device-location .
docker run --env-file .env -p 5000:5000 track-iot-device-location
```

## API Reference

### `GET /devices`

Returns all devices.

```bash
curl http://localhost:5000/devices
```

### `GET /devices/<sim_card_id>`

```bash
curl http://localhost:5000/devices/<sim_card_id>
```

### `GET /devices/<sim_card_id>/location`

```bash
curl http://localhost:5000/devices/<sim_card_id>/location
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
