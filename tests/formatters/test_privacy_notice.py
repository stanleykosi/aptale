from __future__ import annotations

from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aptale.formatters.privacy_notice import (  # noqa: E402
    DEFAULT_LOG_RETENTION_INTERVAL,
    PrivacyNoticeError,
    SUPPORTED_PRIVACY_TRIGGERS,
    render_privacy_notice,
)


def test_render_privacy_notice_for_first_invoice_upload_includes_boundaries() -> None:
    text = render_privacy_notice(trigger="first_invoice_upload")

    assert "*Privacy Notice*" in text
    assert "Before I process your first invoice" in text
    assert "*Sensitive Data Boundaries*" in text
    assert "Supplier names" in text
    assert "raw pricing are treated as sensitive." in text
    assert "*Retention & Flushing*" in text
    assert f"`{DEFAULT_LOG_RETENTION_INTERVAL}`" in text


def test_render_privacy_notice_for_data_handling_request_supports_custom_retention() -> None:
    text = render_privacy_notice(
        trigger="data_handling_request",
        log_retention_interval="14 days",
    )

    assert "data-handling policy" in text
    assert "`14 days`" in text
    assert "*Need Help*" in text
    assert "`privacy`" in text


def test_render_privacy_notice_fails_on_unsupported_trigger() -> None:
    with pytest.raises(PrivacyNoticeError):
        render_privacy_notice(trigger="invoice_quote")


def test_render_privacy_notice_fails_on_blank_retention_interval() -> None:
    with pytest.raises(PrivacyNoticeError):
        render_privacy_notice(
            trigger="first_invoice_upload",
            log_retention_interval="   ",
        )


def test_supported_privacy_triggers_contract() -> None:
    assert SUPPORTED_PRIVACY_TRIGGERS == {"first_invoice_upload", "data_handling_request"}
