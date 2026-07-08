# =============================================================================
# indexer.py — Qdrant indexing for PetroMind Knowledge AI
#
# Key difference from OilMind:
# OilMind used Azure AI Search (managed cloud service)
# PetroMind uses Qdrant (self-hosted Docker container)
# =============================================================================

import os
import sys
import time
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct
)
from google import genai

sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))
from backend.core.config import (
    QDRANT_HOST,
    QDRANT_PORT,
    QDRANT_COLLECTION,
    GEMINI_API_KEY,
    TOP_K_RESULTS
)
from backend.modules.knowledge.chunker import process_all_documents


# Embedding dimensions for gemini-embedding-001
EMBEDDING_DIMENSIONS = 3072


def get_qdrant_client() -> QdrantClient:
    return QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)


def get_embedding(text: str) -> list[float]:
    """
    Generates embedding using Azure OpenAI text-embedding-3-large.
    3072 dimensions — validated in OilMind with 0.77 RAGAS score.
    Credentials loaded from environment variables — never hardcoded.
    """
    from openai import AzureOpenAI
    from backend.core.config import AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_KEY, AZURE_OPENAI_API_VERSION, AZURE_EMBEDDING_DEPLOYMENT

    client = AzureOpenAI(
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_key=AZURE_OPENAI_KEY,
        api_version=AZURE_OPENAI_API_VERSION
    )
    response = client.embeddings.create(
        input=text,
        model=AZURE_EMBEDDING_DEPLOYMENT
    )
    return response.data[0].embedding


def create_qdrant_collection(client: QdrantClient):
    """
    Creates Qdrant collection with vector configuration.
    Skips if collection already exists — idempotent operation.
    """
    existing = [c.name for c in client.get_collections().collections]

    if QDRANT_COLLECTION in existing:
        print(f"✅ Collection '{QDRANT_COLLECTION}' already exists")
        return

    print(f"📋 Creating collection '{QDRANT_COLLECTION}'...")

    client.create_collection(
        collection_name=QDRANT_COLLECTION,
        vectors_config=VectorParams(
            size=EMBEDDING_DIMENSIONS,
            distance=Distance.COSINE
        )
    )

    print(f"✅ Collection created with {EMBEDDING_DIMENSIONS}-dim cosine vectors")


def index_chunks(chunks: list[dict], client: QdrantClient):
    """
    Generates embeddings and uploads to Qdrant in batches of 50.
    Each point has: vector + payload (text, source, page_number).
    """
    print(f"\n🔄 Indexing {len(chunks)} chunks into Qdrant...")
    print(f"   This will take 5-8 minutes\n")

    points = []

    for i, chunk in enumerate(chunks):
        if i % 50 == 0:
            print(f"   Processing {i+1}/{len(chunks)}...")

        embedding = get_embedding(chunk["text"])

        points.append(
            PointStruct(
                id=i,
                vector=embedding,
                payload={
                    "chunk_id": chunk["chunk_id"],
                    "text": chunk["text"],
                    "source": chunk["source"],
                    "page_number": chunk["page_number"],
                    "chunk_index": chunk["chunk_index"]
                }
            )
        )

        time.sleep(0.1)

        if len(points) >= 50:
            client.upsert(
                collection_name=QDRANT_COLLECTION,
                points=points
            )
            points = []

    if points:
        client.upsert(
            collection_name=QDRANT_COLLECTION,
            points=points
        )

    count = client.count(collection_name=QDRANT_COLLECTION)
    print(f"\n✅ {count.count} chunks indexed in Qdrant")


def search_qdrant(query: str, top_k: int = TOP_K_RESULTS) -> list[dict]:
    """
    Searches Qdrant for semantically similar chunks.
    Used by the Knowledge AI agent for retrieval.
    """
    client = get_qdrant_client()
    query_embedding = get_embedding(query)

    results = client.search(
        collection_name=QDRANT_COLLECTION,
        query_vector=query_embedding,
        limit=top_k,
        with_payload=True
    )

    return [
        {
            "text": r.payload["text"],
            "source": r.payload["source"],
            "page_number": r.payload["page_number"],
            "score": r.score
        }
        for r in results
    ]


def run_indexing_pipeline():
    """
    Master function — runs the complete indexing pipeline.
    """
    print("=" * 60)
    print("PetroMind — Knowledge AI Indexing Pipeline")
    print("=" * 60)

    client = get_qdrant_client()

    corpus_dir = os.path.join(
        os.path.dirname(__file__),
        '..', '..', '..', 'corpus', 'raw'
    )

    chunks = process_all_documents(corpus_dir)
    create_qdrant_collection(client)
    index_chunks(chunks, client)

    print("\n" + "=" * 60)
    print("✅ Indexing complete — PetroMind Knowledge AI ready")
    print("=" * 60)


if __name__ == "__main__":
    run_indexing_pipeline()