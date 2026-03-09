# Hermes Constraints For Aptale Implementation

This note captures Hermes-specific constraints that Aptale codegen must honor. Treat these as hard requirements for the canonical current-state path.

## 1) WhatsApp Gateway: Baileys Bot Path

- Hermes WhatsApp support is provided through the built-in Baileys bridge.
- Aptale should use bot mode as the canonical deployment path:
  - `WHATSAPP_ENABLED=true`
  - `WHATSAPP_MODE=bot`
- Enforce platform allowlisting using `WHATSAPP_ALLOWED_USERS` (phone numbers with country code).

## 2) Gateway Authorization Model

- Gateway authorization is allowlist-first and default-deny.
- If no allowlists are configured and `GATEWAY_ALLOW_ALL_USERS` is not set, unauthorized users are denied.
- For Aptale MVP rollout, use explicit allowlists instead of open access.

## 3) Cron Ownership And Delivery

- Scheduled jobs are executed by the Hermes gateway daemon (not an external scheduler).
- Cron jobs can deliver to `origin`, which routes output back to the platform/chat where the job was created.
- For messaging-created jobs, `deliver="origin"` is the canonical delivery mode.

## 4) Delegation Isolation And Limits

- Subagents created by `delegate_task` are isolated and start with fresh conversation context.
- Parent agents must pass exhaustive context in `goal` and `context`; subagents do not inherit parent chat history.
- Delegation depth limit is 2 (parent depth 0, child depth 1; no grandchildren).
- Subagents cannot call:
  - `delegate_task`
  - `clarify`
  - `memory`
  - `send_message`
  - `execute_code`

## 5) Honcho And Built-In Memory Relationship

- Hermes built-in memory (`~/.hermes/memories/USER.md` and `MEMORY.md`) remains primary for local persistent memory.
- Honcho is additive user modeling and does not replace built-in memory.
- Aptale implementations must treat Honcho as a supplement to, not a substitute for, Hermes memory files.
