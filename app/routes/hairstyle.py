from fastapi import APIRouter, UploadFile, File, Form
from app.agents.hairstyle_agent import suggest_hairstyle

router = APIRouter()

@router.post("/style", summary="Suggest hairstyle for face")
async def hairstyle_endpoint(
    file: UploadFile = File(...),
    prompt: str = Form("Suggest best hairstyle")
):
    result = suggest_hairstyle(file, prompt)
    return result
