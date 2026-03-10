from __future__ import annotations

from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aptale.calc.landed_cost import DISCLAIMER_TEXT  # noqa: E402
from aptale.formatters.responses import (  # noqa: E402
    ResponseFormatError,
    render_correction_prompt,
    render_detailed_broker_response,
    render_disclaimer,
    render_short_broker_response,
    render_warning_response,
)


def test_render_short_broker_response_includes_bullets_and_disclaimer() -> None:
    text = render_short_broker_response(
        title="Quick Update",
        lines=["Freight source refreshed", "FX spread widened"],
        disclaimer=DISCLAIMER_TEXT,
    )

    assert "*Quick Update*" in text
    assert "- Freight source refreshed" in text
    assert "- FX spread widened" in text
    assert "*Disclaimer*" in text
    assert DISCLAIMER_TEXT in text


def test_render_detailed_broker_response_renders_sections_and_numbered_next_steps() -> None:
    text = render_detailed_broker_response(
        title="Detailed Brokerage Update",
        summary_lines=["Route validated", "Customs source is official portal"],
        detail_lines=["HS 851712 duty checked", "FX selected rate type is parallel"],
        next_steps=["Confirm HS correction", "Approve quote export"],
    )

    assert "*Detailed Brokerage Update*" in text
    assert "*Details*" in text
    assert "- HS 851712 duty checked" in text
    assert "*Next Step*" in text
    assert "1. Confirm HS correction" in text
    assert "2. Approve quote export" in text


def test_render_warning_response_renders_issue_and_next_steps() -> None:
    text = render_warning_response(
        title="Sourcing Blocked",
        issue="Customs portal is offline right now.",
        next_steps=["Retry later", "Switch to open-web search"],
    )

    assert "*Sourcing Blocked*" in text
    assert "Customs portal is offline right now." in text
    assert "*What You Can Send Next*" in text
    assert "- Retry later" in text
    assert "- Switch to open-web search" in text


def test_render_disclaimer_defaults_to_canonical_text() -> None:
    text = render_disclaimer()
    assert "*Disclaimer*" in text
    assert DISCLAIMER_TEXT in text


def test_render_correction_prompt_includes_confirm_and_examples() -> None:
    text = render_correction_prompt(
        title="Correction Prompt",
        instructions=["Share corrected destination port.", "Share corrected HS code."],
        example_edits=['destination_port = "Tin Can Island"', 'items[0].hs_code = "851712"'],
        confirmation_phrase="Confirmed",
    )

    assert "*Correction Prompt*" in text
    assert "Reply `Confirmed` if no changes are needed." in text
    assert "1. Reply `Confirmed` if no changes are needed." in text
    assert "*Correction Examples*" in text
    assert '`destination_port = "Tin Can Island"`' in text
    assert '`items[0].hs_code = "851712"`' in text


def test_render_short_broker_response_fails_on_blank_title() -> None:
    with pytest.raises(ResponseFormatError):
        render_short_broker_response(title="   ", lines=["ok"])


def test_render_warning_response_fails_on_empty_next_steps() -> None:
    with pytest.raises(ResponseFormatError):
        render_warning_response(
            title="Warning",
            issue="Issue text",
            next_steps=[],
        )
