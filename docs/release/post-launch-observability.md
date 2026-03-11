# Aptale Post-Launch Observability

This guide defines post-launch monitoring expectations for phased beta operation.

## Objectives

- detect WhatsApp/gateway availability issues quickly
- detect authorization drift (unexpected access behavior)
- detect sourcing/export/cron regressions early
- preserve auditability without exposing sensitive invoice data

## Core Signals

## 1) Gateway Availability

Check:

```bash
hermes gateway status
```

Container deployments:

```bash
docker compose ps
docker compose logs --tail=200 aptale-gateway
```

Expected:

- gateway process remains healthy
- no repeated crash/restart loop

## 2) WhatsApp Session Health

Monitor for:

- repeated disconnect/re-pair incidents
- persistent delivery failures
- warning/critical events from `whatsapp-monitor` hook

Action:

- temporary disconnects: monitor for auto-recovery
- persistent failures: run `hermes whatsapp` re-pair flow and restart gateway

## 3) Authorization Integrity

Verify regularly:

- `WHATSAPP_ALLOWED_USERS` matches approved beta list
- `GATEWAY_ALLOW_ALL_USERS` remains `false`/unset

Operational check:

- periodic probe with one authorized and one unauthorized number

## 4) Cron Scheduler Health

Check:

```bash
hermes cron status
hermes cron list
```

Watch for:

- missed/late runs
- repeated failures for alert jobs
- scheduler not running while gateway is online

## 5) Skills & Sourcing Stability

After skills updates:

```bash
hermes skills tap list
./scripts/run_batch_eval.sh
```

Watch for:

- routing/delegation metric regressions
- increased portal outage/CAPTCHA incident rate

## 6) Data & Log Surfaces

Primary paths:

- `~/.hermes/logs/`
- `~/.hermes/sessions/`
- `~/.hermes/state.db`

Policy reminders:

- avoid exporting sensitive raw invoice details into broad operational reports
- rotate/prune logs per runbook policy (`docs/runbooks/log-rotation.md`)

## Recommended Cadence

- daily: gateway status, session health, cron status
- per release: full beta launch checklist + batch eval
- weekly: authorization review, skills tap integrity check, log/session growth review

## Escalation Triggers

Escalate to incident handling when any of the following occurs:

- repeated WhatsApp disconnect loops requiring multiple re-pairs
- unauthorized access behavior deviates from allowlist policy
- cron scheduler stops or alert jobs repeatedly fail
- sourcing outage rate materially impacts quote delivery

Use `docs/runbooks/incident-portal-outage.md` and `docs/runbooks/whatsapp-repair.md` for incident response paths.

