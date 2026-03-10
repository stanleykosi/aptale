# Aptale Access Control Policy (MVP)

This policy defines rollout and authorization rules for Aptale on WhatsApp during MVP.

## Canonical Authorization Path

- Platform: WhatsApp via Hermes gateway
- Mode: `WHATSAPP_MODE=bot`
- Access control: `WHATSAPP_ALLOWED_USERS` explicit allowlist
- Default stance: closed beta only

## Required Environment Controls

- `WHATSAPP_ENABLED=true`
- `WHATSAPP_MODE=bot`
- `WHATSAPP_ALLOWED_USERS=<comma-separated numbers with country code>`
- `GATEWAY_ALLOW_ALL_USERS=false` (or unset)

## Rollout Policy

1. Start with an initial tester allowlist only.
2. Add/remove users by editing `WHATSAPP_ALLOWED_USERS` in `~/.hermes/.env`.
3. Restart gateway after access list updates.
4. Keep list minimal and auditable during MVP.

## Number Format Rules

- Include country code.
- Do not include `+`, spaces, or punctuation.
- Example:
  - `15551234567,447123456789,2348012345678`

## Security Rules

- Do not use `GATEWAY_ALLOW_ALL_USERS=true` for Aptale MVP.
- Do not rely on open access as a fallback.
- If no allowlists are configured, Hermes gateway authorization behavior is default-deny; treat this as expected fail-safe behavior.

## Operational Notes

- Keep allowlist changes versioned in secure ops records.
- Use a dedicated bot number to reduce account exposure and operator error.
