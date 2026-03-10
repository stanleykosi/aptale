# Aptale External Services Setup

This guide covers the Step 8 external service configuration for Aptale:

- OpenRouter provider routing
- Browserbase browser automation
- Honcho user modeling

All secrets belong in `~/.hermes/.env` per Hermes docs.

## 1) OpenRouter Provider Routing

Start from:

- `deploy/env/provider.env.example`

Required env keys:

- `OPENROUTER_API_KEY`
- `HERMES_INFERENCE_PROVIDER=openrouter`
- `HERMES_MODEL=anthropic/claude-3.5-sonnet`

Provider routing policy is configured in `~/.hermes/config.yaml` (not in `.env`):

```yaml
provider_routing:
  sort: "price"
  require_parameters: true
```

Validation checks:

```bash
grep -E '^(OPENROUTER_API_KEY|HERMES_INFERENCE_PROVIDER|HERMES_MODEL)=' ~/.hermes/.env
grep -n 'provider_routing' ~/.hermes/config.yaml
```

Fail-fast behavior:

- If `OPENROUTER_API_KEY` is missing, inference setup is incomplete.
- If provider is not pinned to `openrouter`, Aptale is outside canonical deployment.

## 2) Browserbase Setup

Start from:

- `deploy/env/browserbase.env.example`

Required env keys:

- `BROWSERBASE_API_KEY`
- `BROWSERBASE_PROJECT_ID`
- `BROWSERBASE_PROXIES=true`

Optional tuning keys:

- `BROWSERBASE_ADVANCED_STEALTH`
- `BROWSERBASE_KEEP_ALIVE`
- `BROWSERBASE_SESSION_TIMEOUT`
- `BROWSER_INACTIVITY_TIMEOUT`

Validation checks:

```bash
grep -E '^(BROWSERBASE_API_KEY|BROWSERBASE_PROJECT_ID|BROWSERBASE_PROXIES)=' ~/.hermes/.env
```

Fail-fast behavior:

- If Browserbase credentials are missing, browser tools cannot run.
- If `BROWSERBASE_PROXIES` is not explicitly `true`, Aptale is outside the specified sourcing setup.

## 3) Honcho Setup

Start from:

- `deploy/env/honcho.env.example`

Required env key:

- `HONCHO_API_KEY`

Set workspace in `~/.honcho/config.json`:

```json
{
  "apiKey": "your-honcho-api-key",
  "workspace": "aptale-production",
  "aiPeer": "hermes",
  "environment": "production",
  "saveMessages": true,
  "sessionStrategy": "per-directory",
  "enabled": true
}
```

Validation checks:

```bash
grep '^HONCHO_API_KEY=' ~/.hermes/.env
python - <<'PY'
import json
from pathlib import Path
config = Path.home() / ".honcho" / "config.json"
data = json.loads(config.read_text())
assert data.get("workspace") == "aptale-production", data.get("workspace")
print("honcho workspace ok:", data["workspace"])
PY
```

Fail-fast behavior:

- If `HONCHO_API_KEY` is missing, Honcho integration is unavailable.
- If workspace is not set to `aptale-production`, Aptale profile context may drift across environments.

## 4) Final Verification

After updating env/config files:

```bash
./scripts/check_system.sh
```

This verifies Hermes baseline health before integration tests.
