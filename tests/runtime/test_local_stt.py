from __future__ import annotations

from pathlib import Path
import sys
import types

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aptale.runtime import local_stt  # noqa: E402


def test_transcribe_audio_local_missing_file_returns_error() -> None:
    result = local_stt.transcribe_audio_local("/tmp/aptale-missing-audio.ogg")
    assert result["success"] is False
    assert "not found" in str(result["error"]).lower()


def test_transcribe_audio_local_reports_missing_dependency(tmp_path: Path) -> None:
    audio = tmp_path / "voice.ogg"
    audio.write_bytes(b"not-real-audio")

    sys.modules.pop("faster_whisper", None)
    local_stt._MODEL_CACHE.clear()
    result = local_stt.transcribe_audio_local(str(audio))
    assert result["success"] is False
    assert "faster-whisper" in str(result["error"]).lower()
    assert "pip install" in str(result["error"]).lower()


def test_transcribe_audio_local_success_with_stubbed_model(
    tmp_path: Path, monkeypatch
) -> None:
    audio = tmp_path / "voice.ogg"
    audio.write_bytes(b"fake-audio")

    class _Segment:
        text = "HS code 850440"

    class _Model:
        def transcribe(self, *_args, **_kwargs):
            return ([_Segment()], object())

    fake_module = types.ModuleType("faster_whisper")
    fake_module.WhisperModel = lambda *_args, **_kwargs: _Model()
    monkeypatch.setitem(sys.modules, "faster_whisper", fake_module)
    local_stt._MODEL_CACHE.clear()

    result = local_stt.transcribe_audio_local(str(audio))
    assert result["success"] is True
    assert result["transcript"] == "HS code 850440"
    assert result["provider"] == "local"


def test_install_hermes_transcription_patch_uses_local_provider(monkeypatch) -> None:
    tools_module = types.ModuleType("tools")
    transcription_module = types.ModuleType("tools.transcription_tools")

    def _openai_stub(_file_path: str, model: str | None = None):
        return {"success": False, "transcript": "", "error": "openai unavailable", "model": model}

    transcription_module.transcribe_audio = _openai_stub
    monkeypatch.setitem(sys.modules, "tools", tools_module)
    monkeypatch.setitem(sys.modules, "tools.transcription_tools", transcription_module)
    monkeypatch.setenv("APTALE_LOCAL_STT_ENABLED", "true")
    monkeypatch.setenv("APTALE_STT_PROVIDER", "local")
    monkeypatch.setattr(
        local_stt,
        "transcribe_audio_local",
        lambda file_path, model=None: {
            "success": True,
            "transcript": f"local:{Path(file_path).name}:{model or ''}",
        },
    )

    patched = local_stt.install_hermes_transcription_patch()
    assert patched is True
    result = transcription_module.transcribe_audio("/tmp/voice.ogg", model="small")
    assert result["success"] is True
    assert result["transcript"] == "local:voice.ogg:small"
