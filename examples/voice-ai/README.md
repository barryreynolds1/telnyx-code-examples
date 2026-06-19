# Voice AI Examples — Telnyx

Build AI-powered voice applications on the Telnyx platform. Route inbound calls to AI agents, add real-time AI participants to live calls, build coaching whisper systems, and create automated contact centers.

## Best place to start

**[build-voice-ai-agent-python](../../build-voice-ai-agent-python/)** — Full voice AI agent: inbound call → STT → LLM → TTS, with conversation memory and human transfer.

## What Telnyx Voice AI gives you

- **Call Control API** — Answer, transfer, bridge, record, and conference calls programmatically
- **Media Streaming** — Real-time audio streams for STT/TTS integration
- **AI Assistants** — Managed voice agents with built-in telephony
- **AI Inference** — LLM inference co-located with voice infrastructure for sub-200ms latency
- **Conference Bridge** — Multi-party calls with per-leg audio control
- **TTS** — Text-to-speech at 10x lower cost than ElevenLabs

## Production checklist

- [ ] Webhook endpoint reachable from public internet (use ngrok for dev)
- [ ] Call Control Application configured in [Telnyx Portal](https://portal.telnyx.com/call-control/applications)
- [ ] Error handling for call drops, silence timeouts, and API failures
- [ ] Logging for call IDs, latency, and AI response times
- [ ] Graceful human transfer fallback

## All voice AI examples

| Example | What it does |
|---------|-------------|
| [build-voice-ai-agent](../../build-voice-ai-agent-python/) | Full inbound voice AI agent with STT → LLM → TTS loop |
| [route-phone-calls-to-ai-agent](../../route-phone-calls-to-ai-agent-python/) | Route inbound calls to Telnyx AI Assistant |
| [ai-live-call-participant](../../ai-live-call-participant-python/) | AI joins a live multi-party phone call as a participant |
| [three-way-ai-interpreter](../../three-way-ai-interpreter-python/) | Real-time translation bridge between two callers |
| [ai-sales-coach-whisper](../../ai-sales-coach-whisper-python/) | Live AI coaching whispered to sales rep during calls |
| [warm-transfer-ai-briefing](../../warm-transfer-ai-briefing-python/) | AI summarizes call context before warm transfer |
| [ai-conference-moderator](../../ai-conference-moderator-python/) | AI moderates multi-party conference calls |
| [conference-call-with-ai-summary](../../conference-call-with-ai-summary-python/) | Conference call with automatic AI-generated summary |
| [ai-deposition-assistant](../../ai-deposition-assistant-python/) | AI note-taker for legal depositions |
| [ai-meeting-action-tracker](../../ai-meeting-action-tracker-python/) | Extract action items from conference calls |
| [multi-party-ai-training-call](../../multi-party-ai-training-call-python/) | AI-facilitated group training sessions |
| [deepfake-voice-detector](../../deepfake-voice-detector-python/) | Real-time synthetic voice detection during calls |
| [call-sentiment-live-escalation](../../call-sentiment-live-escalation-python/) | Detect negative sentiment and alert supervisors |
| [real-time-call-intelligence-dashboard](../../real-time-call-intelligence-dashboard-python/) | Live call analytics and sentiment tracking |
| [full-stack-ai-contact-center](../../full-stack-ai-contact-center-python/) | Complete AI-powered contact center |
| [ai-powered-ivr-replacement](../../ai-powered-ivr-replacement-python/) | Replace legacy IVR with conversational AI |
| [build-ivr-phone-menu](../../build-ivr-phone-menu-python/) | Traditional DTMF-based IVR menu |
| [call-whisper-monitoring](../../call-whisper-monitoring-python/) | Supervisor monitoring with whisper |
| [call-queue-with-hold-music](../../call-queue-with-hold-music-python/) | Call queue with hold music and callbacks |
| [programmable-hold-experience](../../programmable-hold-experience-python/) | Dynamic hold experience with tips and trivia |

**Supported languages:** Python, Node.js, Go
