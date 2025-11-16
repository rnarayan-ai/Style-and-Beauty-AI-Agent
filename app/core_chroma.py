from typing import Optional
import chromadb
from app.config import settings

_client: Optional[chromadb.PersistentClient] = None

def get_chroma_client() -> chromadb.PersistentClient:
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=settings.chroma_dir)
    return _client

# exported instance for easy imports
chroma_client = get_chroma_client()