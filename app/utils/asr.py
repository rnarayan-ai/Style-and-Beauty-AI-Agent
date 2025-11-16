import asyncio
from typing import Any, Optional
from app.config import settings
import whisper


_asr_model: Optional[Any] = None


def get_asr_model():
    global _asr_model
    if _asr_model is None:
        _asr_model = whisper.load_model(settings.asr_model)
    return _asr_model


async def transcribe_audio(audio_path: str) -> str:
    model = get_asr_model()
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, lambda: model.transcribe(audio_path))
    text = result.get("text", "").strip()
    text = " ".join(text.split())
    return text