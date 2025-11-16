import chromadb
from chromadb.config import Settings
from langchain_core.documents import Document
from chromadb.utils import embedding_functions
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_community.embeddings import HuggingFaceEmbeddings
#from langchain_openai import OpenAIEmbeddings 
import json, uuid
import os

# Load dataset
with open("data/cheatsheets/cheatsheet_data.json", "r") as f:
    data = json.load(f)
    
# Convert to LangChain documents
docs = [
    Document(
        page_content=item["text"],
        metadata=item["metadata"] | {"id": item["id"], "category": item["category"], "title": item["title"]}
    )
    for item in data
]

# Create or connect to Chroma collection
#db = Chroma(collection_name="makeup_artist_knowledge")
# Add documents
#db.add_documents(docs)
    
# Create or connect to a persistent Chroma collection
CHROMA_DB_DIR = os.getenv("CHROMA_DB_DIR", "./data/cheatsheets/chroma_db")

client = chromadb.Client(Settings(persist_directory=CHROMA_DB_DIR))
embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)
# Use an open-source embedding model (all freeware)

# Create or load the collection for stylist data
collection = client.get_or_create_collection(
    name="beauty_stylist_knowledge",
    embedding_function=embedding_func
)
#collection.add(docs)
print(f"✅ Loaded {len(docs)} makeup knowledge entries into Chroma!")


def ingest_document(content: str, source: str = "manual_upload") -> dict:
    """
    Ingests a text document (like a makeup cheatsheet or stylist PDF)
    into Chroma for RAG-based retrieval.
    """
    doc_id = f"{source}_{len(collection.get()['ids']) + 1}"
    collection.add(documents=[content], ids=[doc_id], metadatas=[{"source": source}])

    return {
        "status": "success",
        "message": f"Document '{doc_id}' ingested successfully.",
        "total_docs": len(collection.get()['ids'])
    }


def get_reference_context(topic: str) -> str:
    """
    Retrieve relevant stylist or makeup knowledge from ChromaDB.
    Used inside makeup_agent.py for LLM reasoning.
    """
    try:
        results = collection.query(
            query_texts=[topic],
            n_results=3
        )

        if not results or not results["documents"]:
            return "No reference knowledge found."

        docs = results["documents"][0]
        context = "\n\n".join(docs)
        return context
    except Exception as e:
        return f"Error retrieving context: {e}"
