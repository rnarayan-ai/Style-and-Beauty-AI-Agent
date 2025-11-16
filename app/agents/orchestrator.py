import asyncio
from typing import Dict
from app.logging_config import logger
from app.agents.rag import retrieve_references
from app.agents.chemist import compute_product_recommendations
from app.agents.hairstyle import hairstyle_agent
from app.agents.makeup import makeup_agent
from app.config import settings


async def orchestrate(payload: Dict) -> Dict:
    vision = payload.get("vision") or {}
    transcript = payload.get("transcript") or payload.get("text") or ""
    language = payload.get("language", "hi")

    refs = await retrieve_references(transcript, vision)
    logger.info("Retrieved %d references", len(refs))

    # Run both use-case agents in parallel (hairstyle + makeup/chemist)
    hair_task = hairstyle_agent(transcript, vision, refs, language)
    makeup_task = makeup_agent(transcript, vision, refs, language)
    hair_out, makeup_out = await asyncio.gather(hair_task, makeup_task)

    def _get_instructions(d: Dict) -> str:
        return d.get("instructions_text") or d.get("instructions") or ""

    instructions = _get_instructions(hair_out) + "\n\n" + _get_instructions(makeup_out)
    products = {**(hair_out.get("products") or {}), **(makeup_out.get("products") or {})}

    safety_note = "\n\n[Safety] Perform a skin patch test before chemical application; check allergies and pregnancy status. Use PPE."
    instructions = instructions + safety_note

    recommended_look = hair_out.get("recommended_look") or makeup_out.get("recommended_look") or "custom"

    return {
        "face_shape": vision.get("face_shape", "unknown"),
        "hair_texture": vision.get("hair_texture", "unknown"),
        "recommended_look": recommended_look,
        "products": products,
        "instructions_text": instructions,
    }