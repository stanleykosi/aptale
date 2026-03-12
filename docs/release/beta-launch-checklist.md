# Aptale Beta Launch Checklist

Use this checklist before admitting each new beta tester.

Status legend:

- `[ ]` pending
- `[x]` complete
- `[n/a]` not applicable for this rollout

## Phase Controls

- [ ] `WHATSAPP_MODE=bot` is set.
- [ ] `GATEWAY_ALLOW_ALL_USERS` is unset or `false`.
- [ ] `WHATSAPP_ALLOWED_USERS` contains only approved beta numbers.
- [ ] Private runbooks and operational docs are access-restricted.

## Access & Authorization

- [ ] One authorized number can message the bot successfully.
- [ ] One unauthorized number is denied.
- [ ] `hermes gateway status` reports healthy service state.

## Alerting & Monitoring Hooks

- [ ] `ADMIN_ALERT_WEBHOOK_URL` is configured (optional but recommended for proactive ops alerts).
- [ ] WhatsApp monitor hook is deployed and active.
- [ ] Test alert path confirms webhook delivery for a simulated disconnect/re-pair event.

## Skills Tap Authentication

- [ ] `GITHUB_PERSONAL_ACCESS_TOKEN` is set in runtime environment.
- [ ] `hermes skills tap list` shows private `aptale-skills` tap.
- [ ] Required Aptale skills are installed from the private tap.

## Browserbase Proxy Validation

- [ ] `BROWSERBASE_PROXIES=true` is configured.
- [ ] Browser tool path executes successfully from gateway runtime.
- [ ] At least one representative sourcing portal request succeeds through Browserbase.

## Honcho Connectivity

- [ ] `HONCHO_API_KEY` is configured (if Honcho is enabled for this stage).
- [ ] Honcho query path responds successfully at runtime.
- [ ] Failure mode is confirmed fail-fast when Honcho credentials are invalid.

## Export Generation Test

- [ ] Landed-cost calculation path succeeds with canonical test payload.
- [ ] CSV export generation succeeds and includes brand footer + disclaimer.
- [ ] PDF export generation succeeds and includes brand footer + disclaimer.
- [ ] WhatsApp attachment delivery succeeds for at least one generated file.

## Cron Alert Smoke Test

- [ ] `hermes cron status` reports scheduler running.
- [ ] A short-interval smoke job is scheduled and visible in `hermes cron list`.
- [ ] Smoke job executes and produces expected result output.
- [ ] Smoke alert delivery returns to origin chat as expected.
- [ ] Smoke job is removed after validation.

## Pre-Admit Decision

- [ ] All required checks above are complete.
- [ ] Open incidents are reviewed and accepted for beta risk.
- [ ] Beta tester onboarding notes are recorded.
