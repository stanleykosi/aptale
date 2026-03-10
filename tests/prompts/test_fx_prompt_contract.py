from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PROMPT_PATH = ROOT / "src" / "aptale" / "prompts" / "subagents" / "fx.md"


def test_fx_prompt_file_exists() -> None:
    assert PROMPT_PATH.is_file()


def test_fx_prompt_requires_open_web_sourcing_behavior() -> None:
    content = PROMPT_PATH.read_text(encoding="utf-8")
    assert "open-web first" in content
    assert "web_search" in content
    assert "web_extract" in content


def test_fx_prompt_requires_official_parallel_labeling() -> None:
    content = PROMPT_PATH.read_text(encoding="utf-8")
    assert "official_rate" in content
    assert "parallel_rate" in content
    assert "rate_type" in content
    assert "`official`" in content
    assert "`parallel`" in content


def test_fx_prompt_enforces_source_attribution_fields() -> None:
    content = PROMPT_PATH.read_text(encoding="utf-8")
    assert "sources" in content
    assert "source_url" in content
    assert "source_title" in content
    assert "retrieved_at" in content
    assert "method" in content


def test_fx_prompt_enforces_json_only_fx_schema_output() -> None:
    content = PROMPT_PATH.read_text(encoding="utf-8")
    assert "fx_quote" in content
    assert "selected_rate_type" in content
    assert "selected_rate" in content
    assert "JSON object only" in content
    assert "Do not call `clarify`." in content
    assert "Do not call `execute_code`." in content
    assert "Do not wrap JSON in markdown code fences." in content
