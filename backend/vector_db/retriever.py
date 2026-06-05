import chromadb

from chromadb.utils import embedding_functions


# ==========================================================
# CONFIG
# ==========================================================
from pathlib import Path

CHROMA_PATH = Path(__file__).resolve().parent / "chroma_db"

client = chromadb.PersistentClient(
    path=str(CHROMA_PATH)
)
COLLECTION_NAME = "latam_compliance"

# Configurable mapping of intents to knowledge bases
KNOWLEDGE_BASES = {
    "COMPLIANCE": "latam_compliance",
    "HR": "hr_playbook"
}

# Same embedding model used during ingestion
embedding_fn = (
    embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
)

# ==========================================================
# CONNECT TO EXISTING CHROMA DB
# ==========================================================

# Initialize both collections safely (creates them if they don't exist yet)
compliance_collection = client.get_or_create_collection(
    name=COLLECTION_NAME,
    embedding_function=embedding_fn
)

hr_collection = client.get_or_create_collection(
    name=KNOWLEDGE_BASES["HR"],
    embedding_function=embedding_fn
)

# Retain 'collection' mapping for backward compatibility
collection = compliance_collection



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

    results = collection.query(
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

    results = collection.query(
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

    results = collection.query(
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

    results = collection.query(
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
    results = compliance_collection.query(
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
    results = hr_collection.query(
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
        embedding_function=embedding_fn
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
