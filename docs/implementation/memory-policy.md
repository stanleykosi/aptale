# Aptale Memory Policy (Step 32)

This document defines the canonical persistence policy for Aptale user
preferences in Hermes built-in memory files.

## Scope

Aptale persists only durable, non-PII preference data:

- `local_currency` (ISO 4217)
- `profit_margin_pct` (0-100)
- `timezone` (IANA/UTC)
- `preferred_routes` (origin/destination country, optional ports/mode)

These values are written to:

- `~/.hermes/memories/USER.md`
- `~/.hermes/memories/MEMORY.md`

## Prohibited Persistence

Do not persist invoice-sensitive fields such as:

- supplier names
- invoice numbers
- raw pricing fields (unit price, subtotal, total)
- line-item invoice payloads
- address/contact invoice metadata

If payload keys indicate PII/raw pricing content, the update path fails fast.

## Canonical Write Path

- `src/aptale/memory/memory_policy.py`
  - validates and normalizes allowed preference fields
  - rejects disallowed PII/raw-pricing keys
- `src/aptale/memory/profile_updates.py`
  - writes sanitized preference snapshots into managed blocks in
    `USER.md` and `MEMORY.md`
  - preserves unrelated file content outside managed markers

## Hermes Alignment

- Built-in Hermes memory (`USER.md`, `MEMORY.md`) is canonical.
- Honcho is additive and not a replacement for operational preference storage.
- Preference persistence is deterministic and local with no fallback side paths.
