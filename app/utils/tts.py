import asyncio
from app.config import settings
import shlex


async def synthesize_text(text: str, out_path: str, lang: str = "hi"):
    voice = settings.tts_voice
    cmd = f"tts --text {shlex.quote(text)} --model_name {voice} --out_path {shlex.quote(out_path)}"
    proc = await asyncio.create_subprocess_shell(cmd)
    await proc.communicate()
    return out_path