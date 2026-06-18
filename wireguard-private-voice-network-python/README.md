# WireGuard Private Voice Network — create WireGuard mesh network for private SIP trunking with encrypted voice traffic.

WireGuard Private Voice Network — create WireGuard mesh network for private SIP trunking with encrypted voice traffic.

## How It Works

```
API Call ──► Your App ──► Telnyx APIs ──► Customer
```

## Environment Variables

| Variable | Type | Format | Required | Description |
|----------|------|--------|----------|-------------|
| `TELNYX_API_KEY` | string | `KEY...` | **yes** | Telnyx API v2 key ([get it](https://portal.telnyx.com/api-keys)) |

## Setup

```bash
cp .env.example .env
pip install -r requirements.txt
python app.py
# Server starts on http://localhost:5000
```

### Docker

```bash
docker build -t wireguard-private-voice-network .
docker run --env-file .env -p 5000:5000 wireguard-private-voice-network
```

## API Reference

### `POST /networks`

Create a new record.

```bash
curl -X POST http://localhost:5000/networks \
  -H "Content-Type: application/json" \
  -d '{
  "name": "f\"voice-net-{int(time.time("
}'
```

### `GET /networks`

Returns all networks.

```bash
curl http://localhost:5000/networks
```

### `POST /interfaces`

Create a new record.

```bash
curl -X POST http://localhost:5000/interfaces \
  -H "Content-Type: application/json" \
  -d '{
  "network_id": "abc-123",
  "region": "ashburn-va"
}'
```

### `POST /peers`

Create a new record.

```bash
curl -X POST http://localhost:5000/peers \
  -H "Content-Type: application/json" \
  -d '{
  "interface_id": "abc-123",
  "public_key": "value",
  "name": "sip-endpoint"
}'
```

### `GET /interfaces/<iface_id>/config`

```bash
curl http://localhost:5000/interfaces/<iface_id>/config
```

### `GET /topology`

```bash
curl http://localhost:5000/topology
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
