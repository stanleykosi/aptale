from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PROMPT_PATH = ROOT / "src" / "aptale" / "prompts" / "subagents" / "freight.md"


def test_freight_prompt_file_exists() -> None:
    assert PROMPT_PATH.is_file()


def test_freight_prompt_requires_browserbase_first_behavior() -> None:
    content = PROMPT_PATH.read_text(encoding="utf-8")
    assert "Browserbase-first" in content
    assert "browser_navigate" in content


def test_freight_prompt_includes_open_web_fallback_instructions() -> None:
    content = PROMPT_PATH.read_text(encoding="utf-8")
    assert "Open-Web Fallback" in content
    assert "web_search" in content
    assert "web_extract" in content
    assert "404/5xx" in content
    assert "CAPTCHA" in content
    assert "source_type" in content
    assert "open_web" in content


def test_freight_prompt_enforces_source_attribution_fields() -> None:
    content = PROMPT_PATH.read_text(encoding="utf-8")
    assert "sources" in content
    assert "source_url" in content
    assert "source_title" in content
    assert "retrieved_at" in content
    assert "method" in content
    assert "browserbase" in content


def test_freight_prompt_enforces_json_only_schema_output() -> None:
    content = PROMPT_PATH.read_text(encoding="utf-8")
    assert "freight_quote" in content
    assert "JSON object only" in content
    assert "Do not wrap JSON in markdown code fences." in content
    assert "Do not call `clarify`." in content
    assert "Do not call `execute_code`." in content
