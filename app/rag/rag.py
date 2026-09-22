from functools import lru_cache
from uuid import uuid4


COLLECTION_NAME = "bank_docs"


@lru_cache
def get_model():
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer("BAAI/bge-small-en-v1.5")


def get_client():
    from app.core.db.qdrant_db import client

    return client


def ensure_collection():
    from qdrant_client.http.models import Distance, VectorParams

    client = get_client()
    if not client.collection_exists(COLLECTION_NAME):
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE)
        )


def ingest_folder(folder_path: str):
    from app.rag.chunking import chunk_text
    from app.rag.pdf_reader import load_pdfs

    ensure_collection()
    model = get_model()
    docs = load_pdfs(folder_path)

    points = []

    for doc in docs:
        chunks = chunk_text(doc["text"])
        embeddings = model.encode(chunks).tolist()

        for chunk, vector in zip(chunks, embeddings):
            points.append({
                "id": str(uuid4()),
                "vector": vector,
                "payload": {
                    "text": chunk,
                    "source": doc["source"]
                }
            })

    get_client().upsert(
        collection_name=COLLECTION_NAME,
        points=points
    )


def retrieve(query: str, k: int = 3):
    ensure_collection()

    query_vector = get_model().encode(query).tolist()
    results = get_client().search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        limit=k
    )

    return [r.payload["text"] for r in results]
