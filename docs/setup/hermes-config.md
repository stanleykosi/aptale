# Aptale Hermes Configuration Baseline

This document defines the canonical Hermes baseline for Aptale. It maps directly to `hermes/config/config.yaml` and should remain minimal until a later implementation step requires additional options.

## Canonical File

- Repository baseline: `hermes/config/config.yaml`
- Deployment target: `~/.hermes/config.yaml`

Copy or symlink the repository file into the Hermes runtime path before starting Aptale.

## Baseline Choices

### `terminal`

- `backend: docker`
  - Uses Hermes containerized terminal execution for safer isolation than host-local command execution.
- `docker_image: "python:3.11-slim"`
  - Matches the Aptale technical specification baseline for Python execution.
- `container_persistent: true`
  - Preserves container filesystem state across sessions, consistent with Hermes container persistence behavior.
- `timeout: 300`
  - Sets terminal command timeout to 300 seconds for long-running sourcing and setup operations.

### `memory`

- `memory_enabled: true`
  - Enables Hermes durable memory behavior for cross-session context.
- `user_profile_enabled: true`
  - Enables Hermes user profile storage (`USER.md` behavior) required by Aptale profiling and preferences.

### `provider_routing`

- `sort: "price"`
  - Uses OpenRouter cost-prioritized provider routing as the canonical baseline.
- `require_parameters: true`
  - Enforces provider compatibility with requested parameters so Aptale avoids silent parameter drops.

### `code_execution`

- `timeout: 300`
  - Sets deterministic max execution time for Hermes code execution runs used by landed-cost calculations.

## Fail-Fast Notes

- If Docker is unavailable, treat setup as blocked and fix the runtime instead of switching to a non-canonical backend.
- If provider routing requirements are unsupported by a provider, update provider selection rather than disabling `require_parameters`.
