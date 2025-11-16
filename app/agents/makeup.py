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


async def makeup_agent(transcript: str, vision: Dict[str, Any], refs: List[Dict[str, Any]], language: str = "hi") -> Dict[str, Any]:
    client = get_groq_client()
    system = (
        "You are a cosmetic makeup advisor. Provide one-line look, numbered steps for beautician, "
        "and conservative product quantity ranges. Include safety checks."
    )
    user = (
        f"User input: {transcript}\n"
        f"Face: {vision.get('face_shape')}\n"
        f"Skin tone: {vision.get('skin_tone')}\n"
        f"References: {[r.get('meta', {}).get('title', '') for r in refs]}"
    )

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
    logger.info("Groq makeup response: %s", text[:400])

    products = {
        "foundation": {"recommended": "BudgetFoundation 30ml", "qty_range": "2-4 ml"},
        "developer": {"recommended": "Local 10 vol", "qty_range": "5-10 ml"},
    }

    return {
        "recommended_look": "Makeup suggestion (Groq)",
        "instructions": text,
        "products": products,
    }