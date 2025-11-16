from fastapi import APIRouter, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
import shutil, os, uuid, tempfile
from app.agents.hairstyle_agent import suggest_hairstyle
from app.agents.makeup_agent import suggest_makeup
from app.core.groq_client import run_groq_query
from app.core.redis_client import redis_client
#from app.core.chroma_client import chroma_client
#from app.utils.sd_generate import generate_endpoint, generate_sdxl_images
import chromadb
chroma_client = chromadb.PersistentClient(path=os.getenv("CHROMA_PATH", "./chroma_data"))


router = APIRouter()

@router.post("/analyze")
async def analyze(
    prompt: str = Form(...),
    file: UploadFile = None
):
    """
    Analyze uploaded selfie + text prompt → return hairstyle & makeup suggestions
    """
    try:
        # Save selfie temporarily
        image_path = None
        if file:
            temp_dir = tempfile.mkdtemp()
            image_path = os.path.join(temp_dir, f"{uuid.uuid4()}_{file.filename}")
            with open(image_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

        # Redis session ID
        session_id = str(uuid.uuid4())
        redis_client.set(f"session:{session_id}:prompt", prompt)
        # Get or create a collection
        collection = chroma_client.get_or_create_collection(name="hairstyle_knowledge")
        # Retrieve reference data from Chroma
        similar_docs = collection.query(
            query_texts=[prompt],
            n_results=3
        )
        print("Similar docs:", similar_docs)

        ref_context = " ".join([d.page_content for d in similar_docs.get('documents', [[]])[0]])

        # Call AI agents
        hairstyle_resp = suggest_hairstyle(prompt, ref_context, image_path)
        makeup_resp = suggest_makeup(prompt, ref_context, image_path)

        # Generate concise explanation via Groq
        summary_prompt = f"""
        Summarize the AI stylist output in friendly tone:
        Hairstyle: {hairstyle_resp}
        Makeup: {makeup_resp}
        Respond in Hinglish if user message was in Hindi.
        """
        final_response = run_groq_query(summary_prompt)
       
        # Cache results
        redis_client.set(f"session:{session_id}:result", final_response)
       # generate_endpoint(hairstyle_resp, background_tasks: BackgroundTasks)
        return JSONResponse({
            "session_id": session_id,
            "hairstyle": hairstyle_resp,
            "makeup": makeup_resp,
            "summary": final_response
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if file:
            try:
                os.remove(image_path)
            except Exception:
                pass
