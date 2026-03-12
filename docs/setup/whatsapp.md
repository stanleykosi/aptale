# Aptale WhatsApp Setup (Bot Mode)

This setup is the canonical Aptale path for MVP: Hermes WhatsApp bridge (Baileys) in `bot` mode with explicit allowlisting.

## Scope

- Supported mode: `WHATSAPP_MODE=bot`
- Access model: explicit `WHATSAPP_ALLOWED_USERS` whitelist
- Not supported for Aptale MVP:
  - Open access (`GATEWAY_ALLOW_ALL_USERS=true`)
  - Alternate legacy auth flows

## 1) Configure Environment

Start from the repository fragment:

- `deploy/env/whatsapp.env.example`

Apply its values into `~/.hermes/.env` and replace example phone numbers with your beta testers.

Required keys:

- `WHATSAPP_ENABLED=true`
- `WHATSAPP_MODE=bot`
- `WHATSAPP_ALLOWED_USERS=<comma-separated E.164-style numbers without +>`

Optional keys for Hermes runtime unification with Aptale codebase:

- `APTALE_QUOTE_LOOP_ENABLED=true`
- `APTALE_REPO_ROOT=/absolute/path/to/aptale`
- `APTALE_DEFAULT_COUNTRY=NG`
- `APTALE_DEFAULT_CURRENCY=NGN`
- `APTALE_DEFAULT_MARGIN_PCT=18`
- `APTALE_DEFAULT_TIMEZONE=Africa/Lagos`
- `APTALE_EXPORT_FORMAT=pdf|csv`
- `APTALE_EXPORT_OUTPUT_DIR=/absolute/path/to/.hermes/runtime/exports`

## 2) Pair the Bot Number

Run:

```bash
hermes whatsapp
```

During pairing:

1. Select bot mode.
2. Use a dedicated WhatsApp number (recommended for clean multi-user bot operation).
3. Confirm the allowlist.
4. Scan QR from WhatsApp Linked Devices.

## 3) Start Gateway

Foreground:

```bash
hermes gateway
```

Service install path:

```bash
hermes gateway install
```

The gateway will start the WhatsApp bridge automatically using the saved session.

## 4) Re-Pair Instructions

If WhatsApp session failures persist after automatic reconnect attempts, re-run:

```bash
hermes whatsapp
```

Then restart gateway.

## 5) Second Number Guidance

Use a dedicated number for bot mode to avoid mixing personal traffic with customer traffic.

Practical options:

- Dual-SIM with WhatsApp Business
- Prepaid SIM used only for bot verification/session

## 6) Fail-Fast Checks

- If `WHATSAPP_ALLOWED_USERS` is missing and open-access flags are not enabled, gateway authorization defaults to deny.
- If bot mode is not set to `WHATSAPP_MODE=bot`, Aptale is outside canonical MVP deployment and should not be promoted.
