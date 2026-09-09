from uuid import uuid4

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    PointStruct,
    VectorParams,
)


QDRANT_URL = "http://127.0.0.1:6333"
COLLECTION_NAME = "documents"

client = QdrantClient(url=QDRANT_URL)


def create_collection() -> None:
    """Create the Qdrant collection if it doesn't exist."""

    collections = client.get_collections()

    collection_names = [
        collection.name
        for collection in collections.collections
    ]

    if COLLECTION_NAME not in collection_names:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=384,
                distance=Distance.COSINE,
            ),
        )


def store_chunks(
    document_id: str,
    filename: str,
    chunks: list[str],
    embeddings: list[list[float]],
) -> None:
    """Store document chunks and embeddings in Qdrant."""

    points = []

    for chunk, embedding in zip(
        chunks,
        embeddings,
    ):
        points.append(
            PointStruct(
                id=str(uuid4()),
                vector=embedding,
                payload={
                    "document_id": document_id,
                    "filename": filename,
                    "text": chunk,
                },
            )
        )

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points,
    )

def search_similar_chunks(
    query_embedding: list[float],
    top_k: int = 3,
) -> list[str]:
    """Find the most relevant chunks for a query embedding."""

    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_embedding,
        limit=top_k,
    ).points

    return [point.payload["text"] for point in results]