# Aptale Context Files Setup

This step defines Aptale's baseline personality and memory seed templates for Hermes.

## Files In This Repository

- `hermes/context/SOUL.md`
- `hermes/context/USER.template.md`
- `hermes/context/MEMORY.template.md`

## How Hermes Uses These Files

### `SOUL.md` (Persona)

- Hermes treats `SOUL.md` as a context file injected into the system prompt at session start.
- Discovery order is:
- `SOUL.md` in the working directory first.
- `~/.hermes/SOUL.md` as fallback.
- Aptale uses this file to enforce broker tone, WhatsApp formatting, HS-code confirmation before quoting, mandatory quote disclaimer usage, and privacy-safe behavior.

### `USER.md` And `MEMORY.md` (Persistent Memory)

- Hermes persistent memory is stored under `~/.hermes/memories/`:
- `USER.md` for user profile facts and preferences.
- `MEMORY.md` for agent operational notes.
- Both are injected as a frozen snapshot at session start and are updated across sessions via Hermes memory behavior.
- Use the repository templates only as onboarding seeds, then maintain the live files in Hermes runtime.

## Aptale Mapping Guidance

- `USER.template.md` covers required merchant profile fields:
- Local currency
- Local timezone
- Route preferences
- Default profit margin
- `MEMORY.template.md` is constrained to non-PII durable operational notes only.

## Deployment Actions

1. Copy `hermes/context/SOUL.md` to `~/.hermes/SOUL.md`.
2. After first onboarding, create:
- `~/.hermes/memories/USER.md` from `hermes/context/USER.template.md`.
- `~/.hermes/memories/MEMORY.md` from `hermes/context/MEMORY.template.md`.

If these files are missing, Aptale should be treated as not fully initialized for production behavior.
