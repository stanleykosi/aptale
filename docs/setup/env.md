# Aptale Environment Contract

Aptale keeps its runtime environment in `~/.hermes/.env` by default, following Hermes conventions. The repository copy at `.env.example` is the canonical list of expected keys for local development and deployment planning.

Use one current-state configuration only. Do not rely on undeclared local variables, silent provider fallbacks, or ad hoc per-machine tweaks.

## Storage Location

- Default Hermes env file: `~/.hermes/.env`
- Optional override: `HERMES_HOME` changes the Hermes runtime root, including where `.env` lives
- Repository example: `.env.example`

## Required Secrets

| Variable | Used by | Failure behavior when missing |
| --- | --- | --- |
| `OPENROUTER_API_KEY` | Hermes model access and OpenRouter-backed tooling | Aptale cannot perform canonical inference; runtime setup is incomplete and should be treated as blocked |
| `BROWSERBASE_API_KEY` | Browserbase browser sessions for freight and customs sourcing | Browser-driven sourcing cannot start; fail fast instead of substituting guessed portal data |
| `BROWSERBASE_PROJECT_ID` | Browserbase project routing | Browser sessions cannot be allocated; fail fast |
| `HONCHO_API_KEY` | Honcho cross-session user modeling | Honcho-backed profile enrichment is unavailable; Aptale should not claim Honcho-powered personalization |
| `GITHUB_PERSONAL_ACCESS_TOKEN` | Private `aptale-skills` tap authentication | Private skills cannot be installed or refreshed via Hermes |

## Required Runtime Configuration

| Variable | Used by | Failure behavior when missing or incorrect |
| --- | --- | --- |
| `WHATSAPP_ENABLED` | Hermes messaging gateway activation | WhatsApp gateway stays disabled, so Aptale cannot operate on its primary user surface |
| `WHATSAPP_MODE` | Hermes WhatsApp bridge mode | Any value other than `bot` is outside the Aptale canonical deployment path |
| `WHATSAPP_ALLOWED_USERS` | WhatsApp allowlist enforcement | Gateway access control is incomplete; do not run Aptale publicly without it |
| `BROWSERBASE_PROXIES` | Browserbase residential proxy behavior | Aptale drifts from the specified sourcing configuration; set it explicitly to `true` rather than relying on defaults |

## Optional Production Variables

| Variable | Used by | Failure behavior when missing |
| --- | --- | --- |
| `APTALE_ADMIN_ALERT_WEBHOOK_URL` | Future admin alerts for gateway/session failures | Operational alerts cannot be delivered to the admin channel |

## Optional Runtime Overrides

| Variable | Used by | Notes |
| --- | --- | --- |
| `HERMES_HOME` | Override Hermes runtime root | Default remains `~/.hermes` |
| `MESSAGING_CWD` | Default terminal working directory for messaging | Helpful for local operator workflows |
| `GATEWAY_ALLOWED_USERS` | Cross-platform gateway allowlist | Not a substitute for `WHATSAPP_ALLOWED_USERS` |
| `GATEWAY_ALLOW_ALL_USERS` | Global allow-all flag | Keep unset or `false` for Aptale |
| `BROWSERBASE_ADVANCED_STEALTH` | Browserbase stealth mode | Optional and plan-dependent on Browserbase side |
| `BROWSERBASE_KEEP_ALIVE` | Browserbase reconnect behavior | Optional tuning only |
| `BROWSERBASE_SESSION_TIMEOUT` | Browserbase session lifetime | Optional tuning only |
| `BROWSER_INACTIVITY_TIMEOUT` | Browser cleanup timeout | Optional tuning only |
| `APTALE_LOCAL_STT_ENABLED` | Enables Aptale runtime patch for local STT | Keep `true` for voice-note support without OpenAI STT |
| `APTALE_STT_PROVIDER` | STT provider selection (`local`, `openai`, `auto`) | Canonical value is `local` for open-source transcription |
| `APTALE_STT_MODEL` | Local faster-whisper model size | `small` is recommended baseline quality/speed |
| `APTALE_STT_DEVICE` | Local STT device selection | Use `auto` unless forcing `cpu` or `cuda` |
| `APTALE_STT_COMPUTE_TYPE` | Local STT quantization mode | `int8` for CPU deployments |
| `APTALE_STT_BEAM_SIZE` | Local STT decoding beam size | `1` is fastest for WhatsApp operations |

## Local Directories Used by Aptale

The bootstrap script creates these canonical directories.

| Path | Purpose |
| --- | --- |
| `~/.hermes/` | Hermes runtime root |
| `~/.hermes/cron/` | Scheduled alert jobs managed by Hermes |
| `~/.hermes/sessions/` | Messaging and agent session state |
| `~/.hermes/logs/` | Local runtime logs |
| `~/.hermes/memories/` | Hermes durable memory files and related state |
| `~/.hermes/skills/` | Installed and tapped skills |
| `~/.hermes/pairing/` | Messaging pairing artifacts |
| `~/.hermes/hooks/` | Hermes event hooks |
| `~/.hermes/image_cache/` | Cached image assets |
| `~/.hermes/audio_cache/` | Cached audio assets |
| `~/.hermes/whatsapp/session/` | Baileys WhatsApp session material |
| `runtime/exports/` | Repository-local export root for generated deliverables |
| `runtime/exports/pdf/` | PDF quote/export staging |
| `runtime/exports/csv/` | CSV breakdown staging |

## Bootstrap

Run the directory bootstrap before local setup that depends on Hermes runtime state:

```bash
./scripts/bootstrap_dirs.sh
```

The script is idempotent. It creates directories only and does not write secrets into `.env`.
