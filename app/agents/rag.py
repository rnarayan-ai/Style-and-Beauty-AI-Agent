from typing import List, Dict, Tuple, Optional
import chromadb
from sentence_transformers import SentenceTransformer
from app.config import settings


_client: Optional[chromadb.PersistentClient] = None
_col = None
_embedder: Optional[SentenceTransformer] = None


def get_chroma_collection() -> Tuple:
    global _client, _col, _embedder
    if _client is None:
        _client = chromadb.PersistentClient(path=settings.chroma_dir)
    try:
        _col = _client.get_collection("stylist_cheats")
    except Exception:
        _col = _client.create_collection("stylist_cheats")
    if _embedder is None:
        _embedder = SentenceTransformer("all-MiniLM-L6-v2")
    return _col, _embedder


async def retrieve_references(query: str, vision: Dict) -> List[Dict]:
    col, embedder = get_chroma_collection()
    q = query or "face recommendation"
    emb = embedder.encode(q).tolist()
    results = col.query(query_embeddings=[emb], n_results=5)
    hits: List[Dict] = []
    if results and results.get("documents"):
        docs = results["documents"][0]
        metas = results.get("metadatas", [])[0] if results.get("metadatas") else []
        for d, m in zip(docs, metas):
            hits.append({"text": d, "meta": m})
    return hits