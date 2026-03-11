# Aptale Runbook: WhatsApp Re-Pair

Use this runbook when WhatsApp delivery stops and the session does not recover automatically.

Hermes/Baileys can recover temporary disconnects. Persistent failures require manual re-pair.

## Trigger Conditions

- persistent `disconnected`/`connection lost` states in gateway logs
- repeated `whatsapp-monitor` critical alerts
- allowlisted users stop receiving responses

## 1) Confirm Gateway State

```bash
hermes gateway status
docker compose logs --tail=200 aptale-gateway
```

## 2) Confirm Runtime Env Is Still Correct

Verify:

- `WHATSAPP_ENABLED=true`
- `WHATSAPP_MODE=bot`
- `WHATSAPP_ALLOWED_USERS` is populated with current beta testers

## 3) Re-Pair Session

```bash
hermes whatsapp
```

Complete QR pairing with the bot number in WhatsApp Linked Devices.

## 4) Restart Gateway

Container runtime:

```bash
docker compose restart aptale-gateway
docker compose logs -f aptale-gateway
```

System service runtime:

```bash
sudo systemctl restart aptale-gateway.service
sudo systemctl status aptale-gateway.service
```

## 5) Validate Recovery

- allowlisted number can send/receive messages
- unauthorized number remains denied
- no ongoing disconnect loop in logs

If failures continue after a fresh pair, escalate as a production incident and check host network stability and WhatsApp account restrictions.

