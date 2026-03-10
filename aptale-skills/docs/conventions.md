# aptale-skills conventions

This file defines baseline conventions for the private Aptale skills repository scaffold.

## Scope
- Keep one canonical current-state instruction path per skill.
- Prefer fail-fast behavior over silent recovery logic.
- Keep routing and extraction instructions in skills, not in ad-hoc prompt text.

## Output Contracts
- Return strict JSON for all extraction and sourcing payloads.
- Include source attribution fields expected by Aptale schemas.
- Reject partial or prose-only outputs for contract-bound steps.

## Safety and Privacy
- Do not include sensitive invoice data in logging instructions.
- Avoid instructions that create compatibility shims or dual behavior for old states.

## Repository Layout
- `SKILL.md`: master routing entrypoint
- `regions/`: region/lane-specific sourcing instructions
- `calculate-landed-cost/`: deterministic calculation/export skill materials
- `docs/`: shared conventions used by skill authors
