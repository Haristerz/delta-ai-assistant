import os
import chromadb
from chromadb.utils import embedding_functions

CHROMA_DIR = os.path.join(os.path.dirname(__file__), "..", "chroma_db")

INTENT_TO_SOURCE = {
    "miles_policy": "miles_policy",
    "baggage":      "baggage_policy",
    "upgrade":      "upgrade_policy",
}

_client     = None
_collection = None

def _get_collection():
    global _client, _collection
    if _collection is None:
        embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        _client     = chromadb.PersistentClient(path=CHROMA_DIR)
        _collection = _client.get_or_create_collection(
            name="delta_policies",
            embedding_function=embedding_fn,
        )
    return _collection


def retrieve(query: str, intent: str, n_results: int = 3) -> str:
    collection = _get_collection()

    source_filter = INTENT_TO_SOURCE.get(intent)

    if source_filter:
        results = collection.query(
            query_texts=[query],
            n_results=n_results,
            where={"source": source_filter},
        )
    else:
        results = collection.query(
            query_texts=[query],
            n_results=n_results,
        )

    documents = results.get("documents", [[]])[0]
    return "\n\n".join(documents)
