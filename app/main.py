import os
import uuid
import aiofiles
from typing import Optional, Dict, Any
from app.utils import sd_generate
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from app.config import settings
from app.utils.asr import transcribe_audio
from app.utils.vision import analyze_image
from app.utils.tts import synthesize_text
from app.agents.orchestrator import orchestrate
from app.logging_config import logger
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from redis import Redis
#from core.chroma_client import ChromaClient
from app.utils.sd_generate import generate_sdxl_images
from dotenv import load_dotenv
import chromadb
import logging
logging.basicConfig(level=logging.INFO)

# Import all route modules
from app.routes import analyze, ingest, hairstyle, makeup

# Load environment variables
load_dotenv()
# Run with below command
# python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 80 --log-level debug
# --- Initialize FastAPI App ---
app = FastAPI(
    title="AI Beauty Stylist",
    description="""
AI-powered hairstyling and makeup recommendation system.

🧠 Features:
- Upload selfies & analyze face shape/skin tone
- Suggest hairstyles & beauty products
- Voice + Hinglish language support
- RAG-powered recommendations (ChromaDB)
- Groq LLM integration
""",
    version="1.0.0"
)

# --- Middleware for CORS ---
origins = [
    "http://localhost:5173",  # React frontend
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Global Resources ---
redis_client = Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", "6379")),
    decode_responses=True
)

chroma_client = chromadb.PersistentClient(path=os.getenv("CHROMA_PATH", "./chroma_data"))

router = APIRouter()

class AnalyzeResponse(BaseModel):
    face_shape: str
    hair_texture: str
    recommended_look: str
    products: Dict[str, Any] = {}
    instructions_text: str = ""
    instructions_audio_url: Optional[str] = None
# .\.venv\Scripts\activate.bat
#python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 80


@app.on_event("startup")
async def startup_event():
    print("🚀 AI Beauty Stylist backend starting...")
    # test redis connection
    try:
        redis_client.ping()
        print("✅ Redis connected")
    except Exception as e:
        print("❌ Redis not connected:", e)

    # test chroma
    try:
        _ = chroma_client.list_collections()
        print("✅ Chroma DB ready")
    except Exception as e:
        print("❌ Chroma not ready:", e)
        
@app.get("/api/health", tags=["System"])
async def health_check():
    return {"status": "ok", "message": "AI Beauty Stylist backend is running","chroma_result":chroma_client.list_collections()}

# Register routes
app.include_router(ingest.router, prefix="/api", tags=["Knowledge Ingestion"])
app.include_router(analyze.router, prefix="/api", tags=["Face Analysis"])
app.include_router(hairstyle.router, prefix="/api", tags=["Hairstyle Suggestions"])
app.include_router(makeup.router, prefix="/api", tags=["Makeup Suggestions"])
app.include_router(sd_generate.router, prefix="/api", tags=["Generate Images"])



@app.get("/")
async def root():
    return {"message": "Hello World"}

@router.post("/generate-images")
def generate_endpoint(prompt: str, background_tasks: BackgroundTasks):
    out_dir = "uploads/sdxl"
    # queue the long-running generation in background
    background_tasks.add_task(generate_sdxl_images, prompt, out_dir, 4)
    return {"status": "queued", "out_dir": out_dir}

#analyze.py is getting used for this function from above router configuration
@app.post("/analyzetest")
async def analyzetest(
    file: UploadFile = File(...),
    audio: UploadFile | None = File(None),
    prompt: str | None = Form(None),
    language: str = Form("en"),
):
    print("Received files:")
    print(file)
    image_path = None
    audio_path = None
    
    if file:
        image_filename = f"{uuid.uuid4().hex}_{file.filename}"
        image_path = os.path.join(settings.upload_dir, image_filename)
        async with aiofiles.open(image_path, "wb") as f:
            await f.write(await file.read())

    if audio:
        audio_filename = f"{uuid.uuid4().hex}_{audio.filename}"
        audio_path = os.path.join(settings.upload_dir, audio_filename)
        async with aiofiles.open(audio_path, "wb") as f:
            await f.write(await audio.read())

    transcript = None
    if audio_path:
        transcript = await transcribe_audio(audio_path)
        logger.info("ASR transcript: %s", transcript)

    vision_features = None
    if image_path:
        vision_features = await analyze_image(image_path)
        logger.info("Vision features: %s", vision_features)

    orchestration_input = {
        "transcript": transcript,
        "text": prompt,
        "vision": vision_features,
        "language": language,
    }

    result = await orchestrate(orchestration_input)

    audio_url = None
    if result.get("instructions_text"):
        audio_filename = f"{uuid.uuid4().hex}_instruction.wav"
        audio_path_out = os.path.join(settings.upload_dir, audio_filename)
        await synthesize_text(result["instructions_text"], audio_path_out, lang=language)
        audio_url = f"/api/audio/{audio_filename}"

    response = AnalyzeResponse(
        face_shape=result.get("face_shape", "unknown"),
        hair_texture=result.get("hair_texture", "unknown"),
        recommended_look=result.get("recommended_look", "custom"),
        products=result.get("products", {}),
        instructions_text=result.get("instructions_text", ""),
        instructions_audio_url=audio_url,
    )
    return response


@router.get("/audio/{filename}")
async def serve_audio(filename: str):
    path = os.path.join(settings.upload_dir, filename)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="audio not found")
    return FileResponse(path, media_type="audio/wav")