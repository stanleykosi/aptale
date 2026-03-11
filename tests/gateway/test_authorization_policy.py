from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WHATSAPP_ENV_EXAMPLE = ROOT / "deploy" / "env" / "whatsapp.env.example"


def test_whatsapp_env_example_enforces_allowlist_only_mvp_defaults() -> None:
    env = _read_env_file(WHATSAPP_ENV_EXAMPLE)

    assert env["WHATSAPP_ENABLED"].lower() == "true"
    assert env["WHATSAPP_MODE"] == "bot"
    assert env["GATEWAY_ALLOW_ALL_USERS"].lower() == "false"

    allowlist = _normalize_allowlist(env.get("WHATSAPP_ALLOWED_USERS", ""))
    assert allowlist == {"15551234567", "447123456789", "2348012345678"}


def test_authorized_number_is_allowed_when_present_in_whatsapp_allowlist() -> None:
    env = _read_env_file(WHATSAPP_ENV_EXAMPLE)

    assert _is_authorized_whatsapp_user("2348012345678", env)
    assert _is_authorized_whatsapp_user("+234 801 234 5678", env)


def test_unauthorized_number_is_denied_under_mvp_closed_beta_policy() -> None:
    env = _read_env_file(WHATSAPP_ENV_EXAMPLE)

    assert not _is_authorized_whatsapp_user("14155550199", env)


def test_gateway_defaults_to_deny_when_no_allowlists_configured() -> None:
    env = {
        "WHATSAPP_ENABLED": "true",
        "WHATSAPP_MODE": "bot",
        "WHATSAPP_ALLOWED_USERS": "",
        "GATEWAY_ALLOWED_USERS": "",
        "GATEWAY_ALLOW_ALL_USERS": "false",
    }

    assert not _is_authorized_whatsapp_user("15551234567", env)


def _is_authorized_whatsapp_user(user_phone: str, env: dict[str, str]) -> bool:
    if _truthy(env.get("GATEWAY_ALLOW_ALL_USERS", "")):
        return True

    platform_allow = _normalize_allowlist(env.get("WHATSAPP_ALLOWED_USERS", ""))
    gateway_allow = _normalize_allowlist(env.get("GATEWAY_ALLOWED_USERS", ""))
    effective_allow = platform_allow | gateway_allow

    # Hermes gateway default-deny behavior when allowlists are absent.
    if not effective_allow:
        return False

    return _canonical_phone(user_phone) in effective_allow


def _read_env_file(path: Path) -> dict[str, str]:
    if not path.is_file():
        raise AssertionError(f"Missing expected env file: {path}")

    out: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        out[key.strip()] = value.strip()
    return out


def _normalize_allowlist(raw: str) -> set[str]:
    if not isinstance(raw, str):
        return set()
    values = [item.strip() for item in raw.split(",")]
    return {_canonical_phone(value) for value in values if value}


def _canonical_phone(value: str) -> str:
    return "".join(ch for ch in str(value) if ch.isdigit())


def _truthy(value: str) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "on"}

