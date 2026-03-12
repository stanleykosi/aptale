"""Python startup hook for Aptale runtime behavior."""

from __future__ import annotations

import os
from pathlib import Path


def _is_enabled(value: str) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


if _is_enabled(os.getenv("APTALE_HERMES_BRIDGE_PATCH", "")):
    hermes_home = Path(os.getenv("HERMES_HOME", str(Path.home() / ".hermes")))
    env_file = hermes_home / ".env"
    if env_file.exists():
        try:
            from dotenv import load_dotenv

            load_dotenv(env_file, override=False)
        except Exception:
            pass
    try:
        from aptale.runtime.local_stt import install_hermes_transcription_patch

        install_hermes_transcription_patch()
    except Exception:
        # STT patching must never block Hermes process boot.
        pass
    try:
        from aptale.runtime.hermes_gateway_patch import install_patch

        install_patch()
    except Exception:
        # Startup patches must never block Hermes process boot.
        pass
