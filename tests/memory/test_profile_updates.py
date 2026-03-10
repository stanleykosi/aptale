from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aptale.memory.profile_updates import (  # noqa: E402
    ProfileUpdateError,
    apply_preference_profile_updates,
)


def _fixed_now() -> datetime:
    return datetime(2026, 3, 10, 12, 0, 0, tzinfo=timezone.utc)


def _valid_preferences() -> dict:
    return {
        "local_currency": "ngn",
        "profit_margin_pct": "18.5",
        "timezone": "Africa/Lagos",
        "preferred_routes": [
            {
                "origin_country": "cn",
                "destination_country": "ng",
                "origin_port": "Guangzhou",
                "destination_port": "Lagos",
                "mode": "sea",
            }
        ],
    }


def test_apply_preference_profile_updates_writes_user_and_memory_files(
    tmp_path: Path,
) -> None:
    memory_dir = tmp_path / "memories"
    result = apply_preference_profile_updates(
        _valid_preferences(), memory_dir=memory_dir, now_fn=_fixed_now
    )

    assert result.user_path == memory_dir / "USER.md"
    assert result.memory_path == memory_dir / "MEMORY.md"
    assert result.user_path.is_file()
    assert result.memory_path.is_file()

    user_text = result.user_path.read_text(encoding="utf-8")
    memory_text = result.memory_path.read_text(encoding="utf-8")

    assert "`NGN`" in user_text
    assert "`18.50`" in user_text
    assert "`Africa/Lagos`" in user_text
    assert "CN -> NG (Guangzhou -> Lagos) [sea]" in user_text

    assert "Aptale Memory Policy Snapshot" in memory_text
    assert "`2026-03-10T12:00:00Z`" in memory_text
    assert "`NGN`" in memory_text
    assert "`18.50`" in memory_text
    assert "`Africa/Lagos`" in memory_text


def test_apply_preference_profile_updates_replaces_managed_blocks_without_clobbering_other_text(
    tmp_path: Path,
) -> None:
    memory_dir = tmp_path / "memories"
    memory_dir.mkdir(parents=True, exist_ok=True)
    user_path = memory_dir / "USER.md"
    memory_path = memory_dir / "MEMORY.md"
    user_path.write_text(
        "# USER.md\n\nOperator Note: keep this.\n\n"
        "<!-- APTALE_USER_PREFERENCES_START -->\nold block\n"
        "<!-- APTALE_USER_PREFERENCES_END -->\n",
        encoding="utf-8",
    )
    memory_path.write_text(
        "# MEMORY.md\n\nKeep this note.\n\n"
        "<!-- APTALE_MEMORY_POLICY_START -->\nold block\n"
        "<!-- APTALE_MEMORY_POLICY_END -->\n",
        encoding="utf-8",
    )

    apply_preference_profile_updates(
        _valid_preferences(), memory_dir=memory_dir, now_fn=_fixed_now
    )

    updated_user = user_path.read_text(encoding="utf-8")
    updated_memory = memory_path.read_text(encoding="utf-8")

    assert "Operator Note: keep this." in updated_user
    assert "Keep this note." in updated_memory
    assert updated_user.count("APTALE_USER_PREFERENCES_START") == 1
    assert updated_user.count("APTALE_USER_PREFERENCES_END") == 1
    assert updated_memory.count("APTALE_MEMORY_POLICY_START") == 1
    assert updated_memory.count("APTALE_MEMORY_POLICY_END") == 1
    assert "old block" not in updated_user
    assert "old block" not in updated_memory


def test_apply_preference_profile_updates_rejects_pii_fields(tmp_path: Path) -> None:
    payload = _valid_preferences()
    payload["supplier_name"] = "Confidential Supplier Ltd"

    with pytest.raises(ProfileUpdateError, match="violates memory policy"):
        apply_preference_profile_updates(payload, memory_dir=tmp_path / "memories")


def test_apply_preference_profile_updates_rejects_invalid_timezone(
    tmp_path: Path,
) -> None:
    payload = _valid_preferences()
    payload["timezone"] = "UTC+1"

    with pytest.raises(ProfileUpdateError, match="violates memory policy"):
        apply_preference_profile_updates(payload, memory_dir=tmp_path / "memories")
