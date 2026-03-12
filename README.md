# Aptale

Aptale is an autonomous AI freight and customs broker built on the Hermes Agent framework. It operates over WhatsApp to ingest invoices, source freight/customs/FX/local-charges/risk data, calculate landed costs, and deliver alerts.

## Architecture At A Glance

- **Core agent runtime:** Hermes Agent (Python 3.11+)
- **Messaging surface:** WhatsApp via Hermes' built-in Baileys bridge
- **Web sourcing:** Browserbase-backed browser workflows plus web sourcing
- **Memory/state:** Hermes memories (`USER.md`, `MEMORY.md`) with Honcho augmentation
- **Skill extensibility:** Private Aptale skills repository consumed by Hermes skills mechanisms

## Hard-Cut Policy

Aptale uses one canonical current-state implementation path:

- No compatibility bridges or migration shims unless explicitly requested
- No silent fallbacks for broken data paths
- Fail-fast diagnostics with explicit user-facing recovery instructions

## WhatsApp-Native, Hermes-First

Aptale is WhatsApp-native and Hermes-first: user interaction stays inside WhatsApp, and orchestration, tooling, memory, and automation are implemented through Hermes conventions.

## Repository Layout

```text
aptale/
├── docs/
│   ├── architecture.md
│   └── decisions/
│       └── ADR-001-canonical-hermes-path.md
├── runtime/
├── tests/
├── fixtures/
└── scripts/
```

## Setup Flow (High Level)

1. Initialize this project as a private Git repository.
2. Keep this repository focused on the canonical Aptale codepath and docs.
3. Continue with subsequent implementation steps for env contracts, Hermes configuration, and runtime setup.
