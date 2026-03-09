# ADR-001: Canonical Hermes-First Path

## Context

Aptale is a WhatsApp-native autonomous freight and customs broker built on Hermes Agent. The product currently targets one canonical current-state implementation rather than multi-version compatibility. The system must ingest sensitive trade documents, source external freight/customs/FX data, and return deterministic outputs without silent degradation.

Hermes conventions define key operational constraints and capabilities:

- WhatsApp messaging is delivered through the built-in Baileys bridge, with bot mode as a primary deployment path.
- Context files (`AGENTS.md`, `SOUL.md`) shape behavior and must remain central to implementation.
- Skills are first-class, progressive-disclosure instruction assets under Hermes.

## Decision

Adopt a single canonical architecture path for Aptale:

1. **Canonical current-state only:** implement one active codepath, with no compatibility bridges, migration shims, or dual behavior for legacy local states.
2. **Fail-fast behavior:** on unavailable portals, persistent CAPTCHA blockage, or invalid upstream data, surface explicit failure and recovery options instead of silent fallback glue.
3. **Hermes-first and WhatsApp-only UX:** keep orchestration in Hermes and keep end-user interactions inside WhatsApp.
4. **Separate private skills boundary:** keep private `aptale-skills` as an external repository concern; do not mix that repository into core runtime codepaths at this stage.

## Consequences

- Implementation remains simpler, auditable, and predictable for early-stage delivery.
- Operational failures are visible immediately, improving trust and debugging speed.
- Teams must update the canonical path directly instead of adding compatibility layers.
- Skill lifecycle and core orchestration lifecycle remain cleanly separated.

## Rejected Alternatives

- **Compatibility-heavy multi-path design:** rejected due to increased complexity, ambiguous behavior, and maintenance overhead.
- **Silent fallback behavior:** rejected because it can hide sourcing/data quality failures and produce untrustworthy outputs.
- **Embedding private skills repo into main runtime codepath now:** rejected to preserve clear ownership boundaries and phased rollout discipline.
