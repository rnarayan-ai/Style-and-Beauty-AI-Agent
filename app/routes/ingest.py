from fastapi import APIRouter, UploadFile, Form, HTTPException
#from app.core.chroma_client import chroma_client
import shutil, os, tempfile, uuid

router = APIRouter()

@router.post("/ingest")
async def ingest_docs(
    category: str = Form(...),   # e.g. "makeup" or "hairstyle"
    file: UploadFile = None
):
    """
    Ingest reference PDF or text/markdown cheatsheet to Chroma vector DB.
    """
    try:
        if not file:
            raise HTTPException(status_code=400, detail="File required")

        # Save temp file
        temp_dir = tempfile.mkdtemp()
        file_path = os.path.join(temp_dir, f"{uuid.uuid4()}_{file.filename}")
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        # Read and store to vector DB
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        collection = chroma_client.get_or_create_collection(name=f"cheatsheet_{category}")
        collection.add(documents=[content], metadatas=[{"category": category}], ids=[str(uuid.uuid4())])

        return {"status": "success", "category": category, "filename": file.filename}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if file:
            try:
                os.remove(file_path)
            except Exception:
                pass
