import os
from sentence_transformers import SentenceTransformer
import chromadb
from app.config import settings


def ingest():
    client = chromadb.PersistentClient(path=settings.chroma_dir)
    try:
        col = client.get_collection('stylist_cheats')
    except Exception:
        col = client.create_collection('stylist_cheats')

    embedder = SentenceTransformer('all-MiniLM-L6-v2')
    base = os.path.join(os.path.dirname(__file__), '..', 'data', 'cheatsheets')
    docs = []
    metas = []
    ids = []

    for fname in os.listdir(base):
        if fname.endswith('.md'):
            path = os.path.join(base, fname)
            with open(path, 'r', encoding='utf8') as f:
                text = f.read()
            ids.append(fname)
            docs.append(text)
            metas.append({'title': fname, 'source': path})

    if docs:
        embeddings = embedder.encode(docs).tolist()
        col.add(ids=ids, documents=docs, metadatas=metas, embeddings=embeddings)


if __name__ == '__main__':
    ingest()