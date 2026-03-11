# Aptale Runbook: Safe Log Cleanup

Use this runbook for safe log cleanup without deleting required Hermes runtime state.

Do not remove active session, pairing, or memory files required for gateway operation.

## Targets

Primary cleanup targets:

- `~/.hermes/logs/`
- old exported run artifacts under `runtime/`

Secondary cleanup (controlled):

- aged session transcript exports in `~/.hermes/sessions/` if retention policy allows

## 1) Pre-Cleanup Safety Steps

```bash
hermes gateway status
```

If possible, run cleanup during a maintenance window.

Create backup archive first:

```bash
mkdir -p ~/aptale-backups
tar -czf ~/aptale-backups/hermes-logs-$(date +%F-%H%M%S).tgz ~/.hermes/logs
```

## 2) Rotate/Prune Logs

Compress logs older than 7 days:

```bash
find ~/.hermes/logs -type f -name '*.log' -mtime +7 -exec gzip -f {} \;
```

Delete compressed logs older than 30 days:

```bash
find ~/.hermes/logs -type f -name '*.gz' -mtime +30 -delete
```

## 3) Session Cleanup (Optional, Policy-Driven)

Use Hermes session tooling where available:

```bash
hermes sessions stats
hermes sessions prune
```

Only prune sessions according to your retention policy and compliance requirements.

## 4) Post-Cleanup Validation

```bash
hermes gateway status
hermes cron status
```

Functional checks:

- allowlisted WhatsApp user still receives responses
- scheduled cron jobs still list correctly (`hermes cron list`)

## Never Delete

- `~/.hermes/.env`
- `~/.hermes/config.yaml`
- `~/.hermes/memories/`
- `~/.hermes/whatsapp/session/`
- `~/.hermes/pairing/`

