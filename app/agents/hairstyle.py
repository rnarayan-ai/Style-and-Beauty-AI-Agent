import os
import asyncio
from groq import Client
from app.config import settings
from app.logging_config import logger
from typing import Any, Dict, List, Optional

_groq: Optional[Client] = None


def get_groq_client() -> Client:
    global _groq
    if _groq is None:
        _groq = Client(api_key=settings.groq_api_key)
    return _groq


async def hairstyle_agent(transcript: str, vision: Dict[str, Any], refs: List[Dict[str, Any]], language: str = "hi") -> Dict[str, Any]:
    client = get_groq_client()
    system = (
        "You are a professional hairstylist assistant. Respond concisely with a recommended haircut "
        "and numbered steps for a local beautician. Provide safe product volume ranges."
    )
    user = (
        f"User input: {transcript}\n"
        f"Face: {vision.get('face_shape')}\n"
        f"Hair: {vision.get('hair_texture')}\n"
        f"References: {[r.get('meta', {}).get('title', '') for r in refs]}"
    )

    # Groq client uses synchronous API; wrap in thread
    def call():
        resp = client.chat.create(
            model="groq-m3-large",
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            max_output_tokens=512,
        )
        return resp

    loop = asyncio.get_event_loop()
    resp = await loop.run_in_executor(None, call)
    text = getattr(resp, "text", str(resp))

    # parse minimally — in production use structured output via JSON schema or tools
    logger.info("Groq hair response: %s", text[:400])

    first_line = text.strip().splitlines()[0] if text else "Haircut suggestion unavailable"
    return {
        "recommended_look": first_line,
        "instructions_text": text,
    }