import chromadb

from chromadb.utils import embedding_functions


# ==========================================================
# CONFIG
# ==========================================================
from pathlib import Path

CHROMA_PATH = Path(__file__).resolve().parent / "chroma_db"

COLLECTION_NAME = "latam_compliance"

# Configurable mapping of intents to knowledge bases
KNOWLEDGE_BASES = {
    "COMPLIANCE": "latam_compliance",
    "HR": "hr_playbook"
}

_client = None
_embedding_fn = None
_compliance_collection = None
_hr_collection = None

def get_chroma_client():
    """
    Lazy-load the Chroma PersistentClient exactly once.
    """
    global _client
    if _client is None:
        print("[DEBUG] Initializing Chroma PersistentClient (should happen once only)")
        _client = chromadb.PersistentClient(
            path=str(CHROMA_PATH)
        )
    return _client

def get_embedding_fn():
    """
    Lazy-load the SentenceTransformer embedding function exactly once.
    """
    global _embedding_fn
    if _embedding_fn is None:
        print("[DEBUG] Initializing SentenceTransformerEmbeddingFunction (should happen once only)")
        _embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
    return _embedding_fn

def get_compliance_collection():
    """
    Lazy-load the compliance collection exactly once.
    """
    global _compliance_collection
    if _compliance_collection is None:
        print("[DEBUG] Loading Compliance Collection from ChromaDB (should happen once only)")
        _compliance_collection = get_chroma_client().get_or_create_collection(
            name=COLLECTION_NAME,
            embedding_function=get_embedding_fn()
        )
    return _compliance_collection

def get_hr_collection():
    """
    Lazy-load the HR collection exactly once.
    """
    global _hr_collection
    if _hr_collection is None:
        print("[DEBUG] Loading HR Collection from ChromaDB (should happen once only)")
        _hr_collection = get_chroma_client().get_or_create_collection(
            name=KNOWLEDGE_BASES["HR"],
            embedding_function=get_embedding_fn()
        )
    return _hr_collection

import time

def init_chroma():
    """
    Eagerly pre-load and initialize the Chroma client, the embedding function, and both collections.
    This should be called at startup to prevent latency on first query.
    """
    print("[DEBUG] Eagerly pre-initializing ChromaDB components on startup...")
    t_start = time.time()
    
    t_client_start = time.time()
    get_chroma_client()
    t_client = time.time() - t_client_start
    print(f"[DEBUG] Chroma client pre-initialized in {t_client:.4f}s")
    
    t_embed_start = time.time()
    get_embedding_fn()
    t_embed = time.time() - t_embed_start
    print(f"[DEBUG] Embedding function pre-initialized in {t_embed:.4f}s")
    
    t_coll_start = time.time()
    get_compliance_collection()
    get_hr_collection()
    t_coll = time.time() - t_coll_start
    print(f"[DEBUG] Collections pre-loaded in {t_coll:.4f}s")
    
    t_total = time.time() - t_start
    print(f"[DEBUG] Pre-initialization completed in {t_total:.4f}s")




# ==========================================================
# FORMAT RESULTS
# ==========================================================

def _format_results(results):
    """
    Convert raw Chroma output into a cleaner structure.
    """

    formatted = []

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    for doc, metadata, distance in zip(
        documents,
        metadatas,
        distances
    ):

        formatted.append(
            {
                "score": round(1 - distance, 4),
                "metadata": metadata,
                "document": doc
            }
        )

    return formatted


# ==========================================================
# GENERIC SEMANTIC SEARCH
# ==========================================================

def search(
    query: str,
    top_k: int = 5
):

    results = get_compliance_collection().query(
        query_texts=[query],
        n_results=top_k
    )

    return _format_results(results)


# ==========================================================
# COUNTRY FILTER SEARCH
# ==========================================================

def search_country(
    query: str,
    country: str,
    top_k: int = 5
):

    results = get_compliance_collection().query(
        query_texts=[query],
        n_results=top_k,
        where={
            "country": country
        }
    )

    return _format_results(results)


# ==========================================================
# COUNTRY + COMPLIANCE FILTER
# ==========================================================

def search_country_compliance(
    query: str,
    country: str,
    compliance_type: str,
    top_k: int = 10
):

    results = get_compliance_collection().query(
        query_texts=[query],
        n_results=top_k,
        where={
            "$and": [
                {
                    "country": country
                },
                {
                    "compliance_type": compliance_type
                }
            ]
        }
    )

    return _format_results(results)


# ==========================================================
# LAW NAME SEARCH
# ==========================================================

def search_law(
    query: str,
    law_name: str,
    top_k: int = 10
):

    results = get_compliance_collection().query(
        query_texts=[query],
        n_results=top_k,
        where={
            "law_name": law_name
        }
    )

    return _format_results(results)


# ==========================================================
# BUILD RAG CONTEXT
# ==========================================================

def build_context(results):

    context_parts = []

    for item in results:

        context_parts.append(
            item["document"]
        )

    return "\n\n".join(
        context_parts
    )


# ==========================================================
# EXTENDED SEARCH UTILITIES
# ==========================================================

def search_compliance(
    query: str,
    top_k: int = 5
):
    """
    Search only the compliance knowledge base (latam_compliance).
    """
    results = get_compliance_collection().query(
        query_texts=[query],
        n_results=top_k
    )
    return _format_results(results)


def search_hr(
    query: str,
    top_k: int = 5
):
    """
    Search only the HR knowledge base (hr_playbook).
    """
    results = get_hr_collection().query(
        query_texts=[query],
        n_results=top_k
    )
    return _format_results(results)


def search_by_collection(
    query: str,
    collection_name: str,
    top_k: int = 5
):
    """
    Search any collection dynamically by name.
    """
    col = client.get_collection(
        name=collection_name,
        embedding_function=get_embedding_fn()
    )
    results = col.query(
        query_texts=[query],
        n_results=top_k
    )
    return _format_results(results)


# ==========================================================
# TESTING
# ==========================================================

if __name__ == "__main__":

    query = "What are labor laws for Chile?"

    results = search(
        query=query,
        top_k=5
    )

    print("\nRESULTS\n")

    for idx, item in enumerate(
        results,
        start=1
    ):

        print("=" * 80)

        print(
            f"Result #{idx}"
        )

        print(
            f"Score: {item['score']}"
        )

        print(
            f"Metadata: {item['metadata']}"
        )

        print(
            f"\nDocument:\n{item['document']}"
        )

        print()

    print("\nRAG CONTEXT\n")

    print(
        build_context(results)
    )
