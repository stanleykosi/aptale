# Aptale Runbook: Portal Outage Incident

Use this runbook for customs/freight sourcing outages (government portal downtime, persistent CAPTCHA blocks, or repeated source timeouts).

Aptale policy is fail-fast: no silent fallback and no guessed quotes.

## 1) Confirm Scope

Identify the affected sourcing leg:

- freight portal
- customs portal
- FX source path

Check recent gateway/session logs and the user-facing failure signal.

## 2) Classify Incident

- **Temporary degradation**: intermittent errors, retries later may succeed.
- **Persistent outage**: repeated hard failures (offline portal, blocking CAPTCHA, long timeout streak).

## 3) User-Facing Handling

For persistent official-source failures:

1. Explicitly state which leg failed.
2. Confirm no estimate was guessed.
3. Offer open-web sourcing where policy permits.

Do not continue with incomplete sourcing payloads for calculation/export.

## 4) Operational Response

1. Record incident start time and affected routes.
2. Capture failing URLs/portal names (avoid sensitive invoice details in notes).
3. If outage is external, monitor for recovery windows and retry.
4. If behavior changed (markup/flow/CAPTCHA), update the relevant skill instructions and redeploy skills.

## 5) Recovery Criteria

Incident can be closed when:

- official source responds consistently again, or
- validated open-web recovery path is operating and documented for the affected lane.

After recovery:

```bash
./scripts/run_batch_eval.sh
```

Then resume normal release flow.

