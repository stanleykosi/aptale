# Aptale Architecture (Canonical Path)

## Scope

This document defines the single canonical Aptale codepath and repository boundaries for the Hermes-first, WhatsApp-native system.

## Canonical End-To-End Codepath

1. User sends invoice content over WhatsApp.
2. Hermes-hosted intake flow performs extraction, translation, and confirmation.
3. Parent orchestration delegates sourcing tasks (freight, customs, FX) with strict JSON contracts.
4. Landed cost calculation runs deterministically from validated structured inputs.
5. Result and disclaimer are returned to the user in WhatsApp.
6. Optional alert criteria are scheduled for proactive monitoring and delivery.

No alternate legacy path is maintained. Failures are surfaced explicitly and immediately.

## Boundary Split

### 1) Main Aptale repository

Owns:

- Orchestration/application code
- Data contracts/schemas
- Tests and fixtures
- Operational scripts
- Architecture/ADR/setup documentation

Does not own:

- Live Hermes home runtime state
- Deployed private skill registry content itself

### 2) Hermes runtime home (`~/.hermes`)

Owns runtime assets and operational state, such as:

- `config.yaml` and `.env`
- memories (`MEMORY.md`, `USER.md`)
- skills directory and hub metadata
- cron jobs, sessions, logs, hooks, and WhatsApp session material

### 3) Separate private `aptale-skills` repository

Owns Aptale-specific reusable skill instruction assets and routing procedures.

- This boundary is represented now.
- Repository scaffolding for that private repo is intentionally deferred to Step 20.

## Hermes Conventions Applied

- WhatsApp is served via Hermes' built-in Baileys bridge with bot mode support.
- Context file behavior is respected: `AGENTS.md` provides project rules; `SOUL.md` defines persona.
- Skills are treated as first-class instruction assets under Hermes' skills system with progressive disclosure.

## Non-Goals

- No external dashboard or web frontend for merchants.
- No dual-path compatibility with historical local states.
- No migration glue, fallback compatibility adapters, or silent recovery branches.
