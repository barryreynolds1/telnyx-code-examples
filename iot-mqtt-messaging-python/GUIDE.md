# MQTT Messaging with Python and Flask

Build a Flask application that manages IoT SIM cards and publishes device data to MQTT brokers.

## How It Works

```
  Client request
        │
        ▼
  ┌────────────────────┐
  │  Python Server      │  receives request
  └─────────┬──────────┘
        │  Telnyx API call
        ▼
  ┌────────────────────┐
  │  Telnyx Messaging │  processes and responds
  └────────────────────┘
```

## Telnyx Products Used

- **Messaging** — [Documentation](https://developers.telnyx.com/docs/messaging)

## Prerequisites

- Python 3.8 or higher.
- A Telnyx account with an active API key from the [Telnyx Portal](https://portal.telnyx.com).
- Active Telnyx IoT SIM cards.
- pip (Python package manager).
- An MQTT broker (local or cloud-based like AWS IoT Core or HiveMQ).

## Step 1: Set Up the Project

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/iot-mqtt-messaging-python
cp .env.example .env
pip install -r requirements.txt
```

Edit `.env` with your Telnyx credentials:

| Variable | Description |
|----------|-------------|
| `TELNYX_API_KEY` | KEY_your_telnyx_api_key_here |
| `FLASK_DEBUG` | your_flask_debug_here |
| `MQTT_BROKER_HOST` | your_mqtt_broker_host_here |
| `MQTT_BROKER_PORT` | your_mqtt_broker_port_here |
| `MQTT_PASSWORD` | your_mqtt_password_here |
| `MQTT_USERNAME` | your_mqtt_username_here |

## Step 2: Understand the Code

The main application logic lives in `app.py`.

### All Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/sims` | API endpoint |
| `GET` | `/sims/<sim_card_id>/usage` | API endpoint |
| `POST` | `/sims/<sim_card_id>/publish` | API endpoint |
| `POST` | `/sims/publish-all` | API endpoint |

## Step 3: Run It

```bash
python app.py
```

The server starts on `http://localhost:5000`.

For webhook-based features, expose your local server:

```bash
ngrok http 5000
```

## Step 4: Test It

```bash
curl http://localhost:5000/sims
```

## Going to Production

- **Environment variables** — never commit API keys; use a secrets manager.
- **Authentication** — protect your endpoints with API key validation.
- **Monitoring** — add structured logging and alerting.
- **Rate limiting** — protect endpoints from abuse.
- **Database** — replace any in-memory storage with a persistent store.

## Resources

- [Source code](https://raw.githubusercontent.com/team-telnyx/telnyx-code-examples/main/iot-mqtt-messaging-python/README.md)
- [API reference](https://raw.githubusercontent.com/team-telnyx/telnyx-code-examples/main/iot-mqtt-messaging-python/API.md)
- [Messaging Documentation](https://developers.telnyx.com/docs/messaging)
- [Telnyx Portal](https://portal.telnyx.com)
