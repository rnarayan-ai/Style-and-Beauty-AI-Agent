from fastapi import APIRouter, UploadFile, File, Form
from app.agents.makeup_agent import suggest_makeup
from app.core.chroma_client import get_reference_context

router = APIRouter()

@router.post("/makeup", summary="Suggest makeup & product application")
async def makeup_endpoint(
    file: UploadFile = File(...),
    prompt: str = Form("Suggest best makeup")
):
    ref_context = get_reference_context("makeup")
    result = suggest_makeup(prompt, ref_context, image_path=file.filename)
    return result
