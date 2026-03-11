# Gateway Resiliency & Authorization Checks

This document defines Step-49 checks for Aptale's WhatsApp gateway assumptions:

- network-drop recovery behavior
- unauthorized-number denial
- allowlist-only MVP enforcement

## Automated Test Checks

Run:

```bash
.venv/bin/python -m pytest -q \
  tests/gateway/test_authorization_policy.py \
  tests/gateway/test_session_monitoring.py
```

Coverage from these tests:

- `test_authorization_policy.py`
  - validates MVP defaults in `deploy/env/whatsapp.env.example`
  - checks explicit allowlist authorization behavior
  - checks denial of unauthorized numbers
  - checks default-deny when no allowlists are configured
- `test_session_monitoring.py`
  - checks disconnect/re-pair conditions produce critical alerts
  - checks recovery events do not raise false alarms
  - checks non-WhatsApp session disconnect noise is ignored
  - checks gateway startup without WhatsApp emits warning alert

## Scripted Manual Checks (Pre-Release)

1. Unauthorized-number denial:
Use one phone number not present in `WHATSAPP_ALLOWED_USERS`.
Send a message to the bot and verify no response is delivered to that user.

2. Allowlist-only MVP enforcement:
Confirm `GATEWAY_ALLOW_ALL_USERS=false` (or unset) and `WHATSAPP_MODE=bot`.
Confirm `WHATSAPP_ALLOWED_USERS` contains only active beta testers.
Restart gateway and verify an allowed number can still reach the bot.

3. Network-drop recovery assumptions:
With gateway running, temporarily disconnect host network, then restore it.
Verify temporary drops recover without manual intervention.
If disconnect state persists, run `hermes whatsapp` to re-pair and confirm hook alerts were emitted.

## Hermes Alignment Notes

- Hermes gateway authorization is default-deny when allowlists are absent.
- WhatsApp bridge (Baileys) can auto-recover temporary disconnects.
- Persistent failures require manual re-pair (`hermes whatsapp`) and should be treated as operational incidents.
