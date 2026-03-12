"""Local speech-to-text integration for Hermes/Aptale voice handling."""

from __future__ import annotations

import logging
import os
from pathlib import Path
import sys
from typing import Any, Optional


logger = logging.getLogger(__name__)

_MODEL_CACHE: dict[tuple[str, str, str], Any] = {}
_PATCHED_ATTR = "_aptale_local_stt_patch_v1"
_SUPPORTED_AUDIO_SUFFIXES = {
    ".aac",
    ".flac",
    ".m4a",
    ".mp3",
    ".mp4",
    ".mpeg",
    ".mpga",
    ".ogg",
    ".opus",
    ".wav",
    ".webm",
}


def _env_name(name: str, default: str) -> str:
    value = str(os.getenv(name, default) or "").strip()
    return value or default


def _resolve_provider() -> str:
    raw = _env_name("APTALE_STT_PROVIDER", "local").lower()
    if raw in {"local", "faster-whisper", "faster_whisper"}:
        return "local"
    if raw == "openai":
        return "openai"
    if raw == "auto":
        return "auto"
    return "local"


def _resolve_model_name(explicit_model: Optional[str]) -> str:
    candidate = str(explicit_model or "").strip()
    if candidate:
        return candidate
    return _env_name("APTALE_STT_MODEL", "small")


def _resolve_device() -> str:
    return _env_name("APTALE_STT_DEVICE", "auto").lower()


def _resolve_compute_type() -> str:
    return _env_name("APTALE_STT_COMPUTE_TYPE", "int8").lower()


def _resolve_beam_size() -> int:
    raw = _env_name("APTALE_STT_BEAM_SIZE", "1")
    try:
        parsed = int(raw)
    except ValueError:
        return 1
    return parsed if parsed > 0 else 1


def _resolve_language() -> str | None:
    language = str(os.getenv("APTALE_STT_LANGUAGE", "") or "").strip().lower()
    return language or None


def _load_model(*, model_name: str, device: str, compute_type: str) -> Any:
    cache_key = (model_name, device, compute_type)
    cached = _MODEL_CACHE.get(cache_key)
    if cached is not None:
        return cached
    # Reduce benign onnxruntime warning noise on CPU-only hosts.
    os.environ.setdefault("ORT_LOG_SEVERITY_LEVEL", "3")
    try:
        from faster_whisper import WhisperModel
    except ImportError as exc:
        raise RuntimeError(
            "Local STT dependency missing: faster-whisper. "
            "Install with: ~/.hermes/hermes-agent/venv/bin/pip install faster-whisper"
        ) from exc

    model = WhisperModel(model_name, device=device, compute_type=compute_type)
    _MODEL_CACHE[cache_key] = model
    return model


def transcribe_audio_local(file_path: str, model: Optional[str] = None) -> dict[str, Any]:
    """Transcribe an audio file with local faster-whisper."""
    path = Path(str(file_path or "").strip())
    if not str(path):
        return {
            "success": False,
            "transcript": "",
            "error": "Audio file path is required.",
            "provider": "local",
        }
    if not path.exists():
        return {
            "success": False,
            "transcript": "",
            "error": f"Audio file not found: {path}",
            "provider": "local",
        }
    if not path.is_file():
        return {
            "success": False,
            "transcript": "",
            "error": f"Audio path is not a file: {path}",
            "provider": "local",
        }
    if path.suffix.lower() not in _SUPPORTED_AUDIO_SUFFIXES:
        return {
            "success": False,
            "transcript": "",
            "error": (
                f"Unsupported audio format: {path.suffix}. "
                f"Supported: {', '.join(sorted(_SUPPORTED_AUDIO_SUFFIXES))}"
            ),
            "provider": "local",
        }

    model_name = _resolve_model_name(model)
    device = _resolve_device()
    compute_type = _resolve_compute_type()
    beam_size = _resolve_beam_size()
    language = _resolve_language()
    try:
        whisper_model = _load_model(
            model_name=model_name,
            device=device,
            compute_type=compute_type,
        )
        segments, _info = whisper_model.transcribe(
            str(path),
            beam_size=beam_size,
            language=language,
            vad_filter=True,
        )
        transcript = " ".join(
            str(getattr(segment, "text", "") or "").strip() for segment in segments
        ).strip()
        if not transcript:
            return {
                "success": False,
                "transcript": "",
                "error": "Local STT returned empty transcript.",
                "provider": "local",
            }
        logger.info("Local STT transcript generated (%d chars)", len(transcript))
        return {
            "success": True,
            "transcript": transcript,
            "provider": "local",
            "model": model_name,
        }
    except Exception as exc:  # pragma: no cover - runtime integration path
        logger.warning("Local STT failed: %s", exc)
        return {
            "success": False,
            "transcript": "",
            "error": f"Local STT failed: {exc}",
            "provider": "local",
        }


def install_hermes_transcription_patch() -> bool:
    """Patch Hermes `tools.transcription_tools.transcribe_audio` to use local STT."""
    enabled = str(os.getenv("APTALE_LOCAL_STT_ENABLED", "true") or "").strip().lower()
    if enabled not in {"1", "true", "yes", "on"}:
        return False

    try:
        import tools.transcription_tools as transcription_tools
    except Exception:
        hermes_home = Path(os.getenv("HERMES_HOME", str(Path.home() / ".hermes")))
        hermes_agent_root = hermes_home / "hermes-agent"
        if hermes_agent_root.exists():
            root_text = str(hermes_agent_root.resolve())
            if root_text not in sys.path:
                sys.path.insert(0, root_text)
        try:
            import tools.transcription_tools as transcription_tools
        except Exception:
            return False

    if getattr(transcription_tools, _PATCHED_ATTR, False):
        return True

    original_transcribe = transcription_tools.transcribe_audio

    def _patched_transcribe_audio(file_path: str, model: Optional[str] = None) -> dict[str, Any]:
        provider = _resolve_provider()
        if provider == "openai":
            return original_transcribe(file_path, model=model)

        local_result = transcribe_audio_local(file_path=file_path, model=model)
        if provider == "local" or bool(local_result.get("success")):
            return local_result

        # Optional explicit auto mode: only try OpenAI when key exists.
        if provider == "auto" and os.getenv("VOICE_TOOLS_OPENAI_KEY"):
            cloud_result = original_transcribe(file_path, model=model)
            if bool(cloud_result.get("success")):
                return cloud_result
            return {
                "success": False,
                "transcript": "",
                "error": (
                    f"Local STT failed: {local_result.get('error', 'unknown')}; "
                    f"OpenAI STT failed: {cloud_result.get('error', 'unknown')}"
                ),
            }
        return local_result

    transcription_tools.transcribe_audio = _patched_transcribe_audio
    setattr(transcription_tools, _PATCHED_ATTR, True)
    return True
