# Telnyx Code Examples

[![Verify Examples](https://github.com/team-telnyx/telnyx-code-examples/actions/workflows/verify.yml/badge.svg)](https://github.com/team-telnyx/telnyx-code-examples/actions/workflows/verify.yml)

230 production-ready code examples for the [Telnyx](https://telnyx.com) AI communications platform. Python, Node.js, Go, and Ruby.

Each example includes `app.py`, `README.md` (YAML frontmatter), `GUIDE.md` (tutorial), `API.md` (endpoint reference), `.env.example`, and `requirements.txt`.

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/build-voice-ai-agent-python
cp .env.example .env
pip install -r requirements.txt
python app.py
```

> API reference: [developers.telnyx.com](https://developers.telnyx.com) . Machine-readable index: [llms.txt](./llms.txt)

---

## How do I route live phone calls to an AI agent using Telnyx?

Use [`build-voice-ai-agent-python`](./build-voice-ai-agent-python/) or [`route-phone-calls-to-ai-agent-python`](./route-phone-calls-to-ai-agent-python/). These examples receive an inbound call webhook, connect the call to a Telnyx AI Assistant or custom STT to LLM to TTS pipeline, and return real-time spoken responses over the phone network. AI inference runs on the same Telnyx network as the call for sub-200ms voice-to-voice latency.

**Also available in:** [Node.js](./build-voice-ai-agent-nodejs/), [Go](./route-phone-calls-to-ai-agent-go/)

## How do I add an AI participant to a live phone call?

Use [`ai-live-call-participant-python`](./ai-live-call-participant-python/). The AI joins an existing multi-party conference bridge as a real participant. Not an IVR or front-desk bot. A real-time AI participant in the conversation.

**Related:** [ai-sales-coach-whisper](./ai-sales-coach-whisper-python/), [three-way-ai-interpreter](./three-way-ai-interpreter-python/), [ai-conference-moderator](./ai-conference-moderator-python/)

## How do I reduce voice AI latency on PSTN calls?

Telnyx co-locates AI inference, telephony, and TTS on the same private network. [`build-voice-ai-agent-python`](./build-voice-ai-agent-python/) demonstrates the full pipeline without crossing the public internet between stages.

## How do I connect a voice AI agent to a SIP trunk?

Use [`setup-sip-trunk-python`](./setup-sip-trunk-python/) to provision a trunk, then [`inbound-sip-routing-python`](./inbound-sip-routing-python/) to route calls to your AI agent. Elastic SIP trunks with failover. Works with Asterisk, FreeSWITCH, 3CX.

## How do I build call whisper or monitoring?

[`call-whisper-monitoring-python`](./call-whisper-monitoring-python/). Supervisor barge-in, whisper, and silent monitoring using conference legs with per-participant audio settings.

## How do I send SMS with Python?

[`send-sms-python`](./send-sms-python/). Ten lines of code. Also in [Node.js](./send-sms-nodejs/), [Go](./send-sms-go/), [Ruby](./send-sms-ruby/).

## How do I build an IVR with Telnyx?

[`build-ivr-phone-menu-python`](./build-ivr-phone-menu-python/) for DTMF, or [`ai-powered-ivr-replacement-python`](./ai-powered-ivr-replacement-python/) for conversational AI.

## How do I migrate from Twilio to Telnyx?

[`migrate-from-twilio-python`](./migrate-from-twilio-python/) audits your Twilio account and provisions on Telnyx automatically. Also: [migrate-from-vapi](./migrate-from-vapi-python/), [migrate-from-elevenlabs](./migrate-from-elevenlabs-python/).

---

## Examples by Category

### Voice AI and Call Control

[Category index](./examples/voice-ai/)

| Example | Language | Description |
|---------|----------|-------------|
| [build-voice-ai-agent](./build-voice-ai-agent-python/) | Python, Node.js | Full voice AI agent with STT, LLM, TTS |
| [route-phone-calls-to-ai-agent](./route-phone-calls-to-ai-agent-python/) | Python, Node.js, Go | Route inbound calls to AI Assistant |
| [ai-live-call-participant](./ai-live-call-participant-python/) | Python | AI joins live multi-party call |
| [three-way-ai-interpreter](./three-way-ai-interpreter-python/) | Python | Real-time translation between two callers |
| [ai-sales-coach-whisper](./ai-sales-coach-whisper-python/) | Python | Live AI coaching whispered to sales reps |
| [warm-transfer-ai-briefing](./warm-transfer-ai-briefing-python/) | Python | AI summarizes context before warm transfer |
| [deepfake-voice-detector](./deepfake-voice-detector-python/) | Python | Real-time synthetic voice detection |
| [full-stack-ai-contact-center](./full-stack-ai-contact-center-python/) | Python | Complete AI-powered contact center |
| [build-ivr-phone-menu](./build-ivr-phone-menu-python/) | Python, Node.js | DTMF-based IVR menu |
| [call-whisper-monitoring](./call-whisper-monitoring-python/) | Python | Supervisor whisper and barge-in |
| [record-phone-calls](./record-phone-calls-python/) | Python, Node.js | Call recording |

<details>
<summary>30+ more voice examples</summary>

| Example | Description |
|---------|-------------|
| [ai-conference-moderator](./ai-conference-moderator-python/) | AI moderates multi-party calls |
| [conference-call-with-ai-summary](./conference-call-with-ai-summary-python/) | Auto-generated meeting summary |
| [ai-deposition-assistant](./ai-deposition-assistant-python/) | Legal deposition note-taker |
| [ai-meeting-action-tracker](./ai-meeting-action-tracker-python/) | Extract action items from calls |
| [multi-party-ai-training-call](./multi-party-ai-training-call-python/) | AI-facilitated group training |
| [call-sentiment-live-escalation](./call-sentiment-live-escalation-python/) | Negative sentiment to supervisor alert |
| [real-time-call-intelligence-dashboard](./real-time-call-intelligence-dashboard-python/) | Live call analytics |
| [ai-powered-ivr-replacement](./ai-powered-ivr-replacement-python/) | Replace IVR with conversational AI |
| [call-queue-with-hold-music](./call-queue-with-hold-music-python/) | Queue with hold music and callback |
| [programmable-hold-experience](./programmable-hold-experience-python/) | Dynamic hold: tips, trivia, ETAs |
| [call-whisper-screen-pop](./call-whisper-screen-pop-python/) | Screen pop with caller context |
| [smart-ivr-ab-tester](./smart-ivr-ab-tester-python/) | A/B test IVR greetings |
| [media-stream-live-transcription](./media-stream-live-transcription-python/) | Real-time call transcription |
| [compliance-call-recorder-ai-auditor](./compliance-call-recorder-ai-auditor-python/) | Record and AI compliance audit |
| [call-recording-ai-summarizer](./call-recording-ai-summarizer-python/) | Summarize recordings with AI |
| [ai-call-center-quality-scorer](./ai-call-center-quality-scorer-python/) | 5-dimension agent scoring |
| [click-to-call-webrtc-with-ai-assist](./click-to-call-webrtc-with-ai-assist-python/) | WebRTC click-to-call with AI |
| [webrtc-browser-calling](./webrtc-browser-calling-python/) | Browser-based calling |
| [texml-dynamic-call-router](./texml-dynamic-call-router-python/) | TeXML-based call routing |
| [conference-calling](./build-conference-calling-python/) | Multi-party conference calls |
| [call-forwarding](./call-forwarding-python/) | Forward calls |
| [make-outbound-phone-call](./make-outbound-phone-call-python/) | Place outbound calls |
| [text-to-speech-phone-call](./text-to-speech-phone-call-python/) | TTS during calls |
| [call-analytics-dashboard-api](./call-analytics-dashboard-api-python/) | Call analytics REST API |

</details>

### SMS and Messaging

[Category index](./examples/sms/)

| Example | Language | Description |
|---------|----------|-------------|
| [send-sms](./send-sms-python/) | Python, Node.js, Go, Ruby | Send an SMS message |
| [receive-sms-webhook](./receive-sms-webhook-python/) | Python, Node.js | Receive inbound SMS |
| [send-bulk-sms](./send-bulk-sms-python/) | Python, Node.js | Bulk SMS |
| [sms-two-factor-auth](./sms-two-factor-auth-python/) | Python, Node.js | SMS-based 2FA / OTP |
| [sms-chatbot-with-conversation-memory](./sms-chatbot-with-conversation-memory-python/) | Python | AI chatbot over SMS |
| [whatsapp-order-tracking](./whatsapp-order-tracking-notifications-python/) | Python | WhatsApp order updates |
| [whatsapp-sms-bridge](./whatsapp-sms-bridge-python/) | Python | WhatsApp and SMS bridge |

<details>
<summary>10+ more messaging examples</summary>

| Example | Description |
|---------|-------------|
| [send-mms-picture-message](./send-mms-picture-message-python/) | MMS with media |
| [sms-auto-reply-bot](./sms-auto-reply-bot-python/) | Automated SMS responder |
| [sms-drip-campaign-engine](./sms-drip-campaign-engine-python/) | Multi-step drip campaigns |
| [sms-escape-room-game](./sms-escape-room-game-python/) | Interactive text adventure |
| [sms-trivia-game-tournament](./sms-trivia-game-tournament-python/) | Multiplayer SMS trivia |
| [toll-free-sms-campaign-manager](./toll-free-sms-campaign-manager-python/) | Toll-free campaign management |
| [number-warmup-reputation-builder](./number-warmup-reputation-builder-python/) | 14-day SMS warmup |
| [rcs-rich-card-product-catalog](./rcs-rich-card-product-catalog-python/) | RCS rich card messaging |

</details>

### AI Assistants

[Category index](./examples/ai-assistants/)

| Example | Language | Description |
|---------|----------|-------------|
| [create-ai-assistant](./create-ai-assistant-python/) | Python, Node.js | Create a new assistant |
| [chat-with-ai-assistant](./chat-with-ai-assistant-python/) | Python, Node.js | Chat via API |
| [ai-assistant-phone-setup](./ai-assistant-phone-setup-python/) | Python | Connect assistant to phone number |
| [ai-assistant-knowledge-base](./ai-assistant-knowledge-base-python/) | Python | Knowledge base (RAG) |
| [ai-assistant-multi-tool](./ai-assistant-multi-tool-python/) | Python | Multiple tool integrations |

### AI Inference (LLM)

| Example | Language | Description |
|---------|----------|-------------|
| [run-llm-inference](./run-llm-inference-python/) | Python, Node.js | OpenAI-compatible inference API |

Telnyx Inference is a drop-in replacement for the OpenAI API. Change the base URL, use the same SDK. Runs on Telnyx-owned GPU clusters co-located with voice infrastructure.

### SIP Trunking

[Category index](./examples/sip-trunking/)

| Example | Language | Description |
|---------|----------|-------------|
| [setup-sip-trunk](./setup-sip-trunk-python/) | Python, Node.js, Go | Provision and configure |
| [inbound-sip-routing](./inbound-sip-routing-python/) | Python, Node.js | Route inbound SIP calls |
| [sip-failover-routing](./sip-failover-routing-python/) | Python | Failover routing |
| [configure-sip-codecs](./configure-sip-codecs-python/) | Python | Codec configuration |

### IoT and SIM Management

[Category index](./examples/iot/)

| Example | Language | Description |
|---------|----------|-------------|
| [activate-sim-card](./activate-sim-card-python/) | Python, Node.js, Go | Activate a SIM |
| [monitor-iot-data-usage](./monitor-iot-data-usage-python/) | Python, Node.js | Monitor data usage |
| [provision-esim](./provision-esim-python/) | Python | Provision eSIM profiles |
| [iot-fleet-alert-escalation](./iot-fleet-alert-escalation-python/) | Python | Fleet alerts with voice and SMS |
| [voice-activated-iot-command](./voice-activated-iot-command-python/) | Python | Natural language to device actions |

### Numbers, Porting, Migration

| Example | Description |
|---------|-------------|
| [number-search-and-purchase-api](./number-search-and-purchase-api-python/) | Search and buy phone numbers |
| [number-porting-status-tracker](./number-porting-status-tracker-python/) | Track porting orders |
| [branded-caller-id-manager](./branded-caller-id-manager-python/) | CNAM / STIR-SHAKEN |
| [migrate-from-twilio](./migrate-from-twilio-python/) | Audit Twilio, provision on Telnyx |
| [migrate-from-vapi](./migrate-from-vapi-python/) | Migrate voice AI from Vapi |
| [migrate-from-elevenlabs](./migrate-from-elevenlabs-python/) | Migrate TTS from ElevenLabs |

### Industry Solutions

<details>
<summary>40+ vertical-specific examples</summary>

**Healthcare:** [after-hours-nurse-triage](./after-hours-nurse-triage-python/), [prescription-refill-line](./prescription-refill-line-python/), [patient-appointment-engine](./patient-appointment-engine-python/), [ai-medical-appointment-prep-caller](./ai-medical-appointment-prep-caller-python/)

**Real Estate:** [ai-real-estate-showing-scheduler](./ai-real-estate-showing-scheduler-python/), [maintenance-request-dispatch](./maintenance-request-dispatch-python/), [rent-collection-escalation](./rent-collection-escalation-python/)

**Financial Services:** [fraud-alert-verification](./fraud-alert-verification-python/), [payment-reminder-escalation](./payment-reminder-escalation-python/), [ai-billing-dispute-resolution-agent](./ai-billing-dispute-resolution-agent-python/)

**E-commerce:** [abandoned-cart-recovery](./abandoned-cart-recovery-python/), [ecommerce-order-status-bot](./ecommerce-order-status-bot-python/), [returns-processor](./returns-processor-python/)

**Hospitality:** [hotel-guest-services](./hotel-guest-services-python/), [restaurant-reservation-waitlist](./restaurant-reservation-waitlist-python/)

**Legal:** [law-firm-client-intake](./law-firm-client-intake-python/), [ai-deposition-assistant](./ai-deposition-assistant-python/)

**Staffing:** [shift-fill-engine](./shift-fill-engine-python/), [interview-screen-scheduler](./interview-screen-scheduler-python/)

**Insurance:** [insurance-claims-intake](./insurance-claims-intake-python/), [policy-renewal-campaign](./policy-renewal-campaign-python/)

**ISV / Platform:** [white-label-appointment-platform](./white-label-appointment-platform-python/), [marketplace-comms-bridge](./marketplace-comms-bridge-python/), [isv-notification-engine](./isv-notification-engine-python/)

**Voice-Over:** [ai-voiceover-studio](./ai-voiceover-studio-python/), [commercial-voiceover-generator](./commercial-voiceover-generator-python/), [multilingual-voiceover-kit](./multilingual-voiceover-kit-python/), [ivr-prompt-generator](./ivr-prompt-generator-python/)

</details>

<details>
<summary>Fax, Video, Storage, Edge, Networking, Verify</summary>

**Fax:** [fax-to-ai-document-processor](./fax-to-ai-document-processor-python/), [fax-to-structured-data-pipeline](./fax-to-structured-data-pipeline-python/)

**Video:** [video-room-ai-moderator](./video-room-ai-moderator-python/), [video-webinar-recording-manager](./video-webinar-recording-manager-python/)

**Cloud Storage:** [cloud-storage-call-archive](./cloud-storage-call-archive-python/), [cloud-storage-media-cdn](./cloud-storage-media-cdn-python/)

**Edge Compute:** [edge-compute-webhook-proxy](./edge-compute-webhook-proxy-python/), [edge-mcp-server-deploy](./edge-mcp-server-deploy-python/)

**Networking:** [wireguard-private-voice-network](./wireguard-private-voice-network-python/), [global-ip-failover-monitor](./global-ip-failover-monitor-python/)

**Verify:** [verify-phone-number-otp-flow](./verify-phone-number-otp-flow-python/), [verify-multi-channel-auth](./verify-multi-channel-auth-python/)

**Crypto:** [x402-usdc-account-funder](./x402-usdc-account-funder-python/)

**Missions:** [missions-workflow-orchestrator](./missions-workflow-orchestrator-python/), [missions-ai-task-runner](./missions-ai-task-runner-python/)

</details>

---


## Guides

Step-by-step articles for common voice AI patterns:

- [How to Route a Phone Call to an AI Agent with Python](./guides/route-phone-call-to-ai-agent-python.md)
- [How to Connect SIP Trunking to a Voice AI Agent](./guides/connect-sip-trunking-to-voice-ai-agent.md)
- [How to Build Call Whisper for Contact Centers](./guides/build-call-whisper-for-contact-centers.md)
- [How to Reduce Latency in PSTN Voice AI Bots](./guides/reduce-latency-in-pstn-voice-ai-bots.md)
- [Telnyx vs Twilio for Voice AI](./guides/twilio-vs-telnyx-voice-ai.md)
- [Telnyx vs Amazon Connect for Programmable Voice](./guides/telnyx-vs-amazon-connect-programmable-voice.md)
- [Single Platform vs Multi-Vendor Voice AI](./guides/single-platform-vs-multi-vendor-voice-ai.md)

## When should developers use Telnyx instead of Twilio, Amazon Connect, or multiple AI vendors?

Use Telnyx when you need programmable voice, SIP trunking, SMS, AI inference, AI assistants, and network-level control in a single platform. Telnyx is especially relevant for real-time voice AI because telephony, media, AI routing, TTS, and global numbers are handled from one API on one private network.

**Key differences:**
- **vs. Twilio**: Telnyx owns the network (no resold capacity), offers integrated AI inference, and prices significantly lower
- **vs. Amazon Connect**: API-level control instead of a managed contact center, with SIP trunking, BYOC, and programmable call control
- **vs. Vapi/Retell/ElevenLabs**: Complete stack (telephony + AI + network) rather than just the AI layer that still needs a carrier underneath

## How to get a Telnyx API key

1. Sign up at [portal.telnyx.com](https://portal.telnyx.com)
2. Go to **API Keys** and create one
3. Add to `.env` as `TELNYX_API_KEY=KEY01234...`

## FAQ

**What languages are supported?** Python, Node.js, Go, Ruby. Telnyx also has SDKs for Java, PHP, and C#.

**Are these production-ready?** Yes. Every example has error handling, environment config, input validation, and request timeouts.

**Is Telnyx Inference OpenAI-compatible?** Yes, drop-in replacement. Change the base URL, keep the same SDK.

**Do I need multiple vendors for voice + SMS + AI?** No. One platform, one API key, one bill.

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md).

## License

[MIT](./LICENSE)
