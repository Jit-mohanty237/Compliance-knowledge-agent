import chromadb

from chromadb.utils import embedding_functions


from pathlib import Path

CHROMA_PATH = Path(__file__).resolve().parent / "chroma_db"

client = chromadb.PersistentClient(
    path=str(CHROMA_PATH)
)
COLLECTION_NAME = "latam_compliance"


embedding_fn = (
    embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
)

client = chromadb.PersistentClient(
    path=CHROMA_PATH
)


collection = client.get_collection(
    name=COLLECTION_NAME,
    embedding_function=embedding_fn
)


def semantic_search(
    query,
    top_k=5
):

    result = collection.query(
        query_texts=[query],
        n_results=top_k
    )

    return result


def country_search(
    query,
    country,
    top_k=10
):

    result = collection.query(
        query_texts=[query],
        n_results=top_k,
        where={
            "country": country
        }
    )

    return result


def country_compliance_search(
    query,
    country,
    compliance_type,
    top_k=10
):

    result = collection.query(
        query_texts=[query],
        n_results=top_k,
        where={
            "$and": [
                {
                    "country": country
                },
                {
                    "compliance_type":
                        compliance_type
                }
            ]
        }
    )

    return result


if __name__ == "__main__":

    query = input(
        "Ask compliance question: "
    )

    results = semantic_search(
        query=query,
        top_k=5
    )

    print("\nRESULTS\n")

    for doc in results["documents"][0]:

        print("=" * 60)
        print(doc)
        print()
