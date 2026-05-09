import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import chromadb
from chromadb.utils import embedding_functions

POLICIES_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "policies")
CHROMA_DIR   = os.path.join(os.path.dirname(__file__), "..", "chroma_db")

POLICY_FILES = {
    "miles_policy":   "miles_policy.txt",
    "baggage_policy": "baggage_policy.txt",
    "upgrade_policy": "upgrade_policy.txt",
}

def read_policy(filename: str) -> str:
    path = os.path.join(POLICIES_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    chunks = []
    start  = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end].strip())
        start += chunk_size - overlap
    return [c for c in chunks if c]

def ingest():
    print("Starting policy ingestion into ChromaDB...")

    embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )

    client     = chromadb.PersistentClient(path=CHROMA_DIR)
    collection = client.get_or_create_collection(
        name="delta_policies",
        embedding_function=embedding_fn,
    )

    for policy_name, filename in POLICY_FILES.items():
        print(f"  Processing {filename}...")
        text   = read_policy(filename)
        chunks = chunk_text(text)

        ids       = [f"{policy_name}_chunk_{i}" for i in range(len(chunks))]
        metadatas = [{"source": policy_name, "chunk_index": i} for i in range(len(chunks))]

        collection.upsert(
            ids=ids,
            documents=chunks,
            metadatas=metadatas,
        )
        print(f"    Stored {len(chunks)} chunks from {filename}")

    print(f"\nIngestion complete. Total documents in collection: {collection.count()}")


if __name__ == "__main__":
    ingest()
