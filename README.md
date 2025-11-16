import osty Stylist (Groq + Chroma + Redis) - Project
from sentence_transformers import SentenceTransformer
import chromadb
from app.config import settings
1. Copy files to a repo directory.
2. Create `.env` from `.env.example` and set `API_KEY`.
def ingest():ices with `docker-compose up --build`.
    client = chromadb.PersistentClient(path=settings.chroma_dir).
    try:
        col = client.get_collection('stylist_cheats')
    except Exception:integration
        col = client.create_collection('stylist_cheats')nt. Ensure `API_KEY` is set in env.
    embedder = SentenceTransformer('all-MiniLM-L6-v2')or production, prefer structured responses (JSON schema) or tools to parse output.
    base = os.path.join(os.path.dirname(__file__), '..', 'data', 'cheatsheets')
    docs = []
    metas = []
    ids = []p provides conservative ranges only. Do not rely on the app for medical/dermatological diagnoses. Include clear T&Cs and training for salon partners.
    for fname in os.listdir(base):
        if fname.endswith('.md'):
            path = os.path.join(base, fname)
            with open(path, 'r', encoding='utf8') as f:ceMesh + hair segmentation for production.
                text = f.read()imple chroma collection creation with an ingestion script (below) that loads `data/cheatsheets` into Chroma with metadata.
            ids.append(fname)uning or using structured output (Groq + JSON schema or function calling, if supported) to guarantee predictable fields.            docs.append(text)            metas.append({'title': fname, 'source': path})    embeddings = embedder.encode(docs).tolist()    col.add(ids=ids, documents=docs, metadatas=metas, embeddings=embeddings)if __name__ == '__main__':    ingest()