# SIP Trunking Examples — Telnyx

Connect your PBX, SBC, or voice infrastructure to the Telnyx network with elastic SIP trunks.

## Best place to start

**[setup-sip-trunk-python](../../setup-sip-trunk-python/)** — Provision a SIP trunk and configure credentials.

## What Telnyx SIP Trunking gives you

- **Elastic SIP trunks** — No capacity limits, pay per use
- **Failover routing** — Automatic failover between endpoints
- **Codec control** — Configure Opus, G.722, G.711, and more
- **Global coverage** — Local numbers in 60+ countries
- **BYOC** — Bring your own carrier for existing infrastructure

## Production checklist

- [ ] SIP Connection configured with authentication credentials
- [ ] Failover endpoints configured for redundancy
- [ ] Codec preferences set for your use case
- [ ] Firewall allows Telnyx SIP signaling IPs
- [ ] Call routing rules tested for inbound and outbound

## All SIP trunking examples

| Example | What it does |
|---------|-------------|
| [setup-sip-trunk](../../setup-sip-trunk-python/) | Provision and configure a SIP trunk |
| [inbound-sip-routing](../../inbound-sip-routing-python/) | Route inbound SIP calls |
| [sip-failover-routing](../../sip-failover-routing-python/) | Configure failover routing |
| [configure-sip-codecs](../../configure-sip-codecs-python/) | Set codec preferences |
| [sip-load-balancer-health-check](../../sip-load-balancer-health-check-python/) | Health check SIP endpoints |
| [sip-trunking-failover-monitor](../../sip-trunking-failover-monitor-python/) | Monitor failover events |

**Supported languages:** Python, Node.js, Go
