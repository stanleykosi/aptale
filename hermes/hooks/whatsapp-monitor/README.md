# WhatsApp Monitor Hook

This Hermes hook monitors WhatsApp/Baileys session health and sends admin alerts to a webhook when re-pairing risk is detected.

## Behavior

- Subscribes to:
  - `gateway:startup`
  - `session:start`
- Sends an alert when:
  - Gateway starts without `whatsapp` in active platforms.
  - Session event context indicates disconnect/re-pair conditions (for example: disconnect, logged out, QR/pairing required).

The alert payload includes a repair action:

- `Run hermes whatsapp and re-pair the WhatsApp session if failures persist.`

This follows Hermes WhatsApp guidance: temporary disconnections can auto-recover, while persistent failures require re-pairing.

## Required Environment

- `ADMIN_ALERT_WEBHOOK_URL` (PagerDuty/Slack-compatible webhook endpoint)

If an alert condition is detected and this variable is missing, the hook raises an explicit runtime error so the issue is visible in gateway logs.

## Runtime Registration

Create `~/.hermes/hooks/whatsapp-monitor/HOOK.yaml`:

```yaml
name: whatsapp-monitor
description: Alert admin webhook on WhatsApp disconnect or re-pair conditions
events:
  - gateway:startup
  - session:start
```

Hermes loads this hook in gateway mode and calls `handle(event_type, context)`.
