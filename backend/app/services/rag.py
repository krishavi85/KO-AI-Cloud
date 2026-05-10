from uuid import uuid4
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, FieldCondition, Filter, MatchValue, PointStruct, VectorParams
from app.config import settings
from app.services.ollama_client import embed

client = QdrantClient(url=settings.QDRANT_URL)


def ensure_collection(vector_size: int):
    names = [c.name for c in client.get_collections().collections]
    if settings.RAG_COLLECTION not in names:
        client.create_collection(
            collection_name=settings.RAG_COLLECTION,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
        )


def index_chunks(user_id: int, document_id: int, filename: str, chunks: list[str]) -> int:
    points = []
    first_vector = None
    for idx, chunk in enumerate(chunks):
        vector = embed(chunk)
        if not vector:
            continue
        if first_vector is None:
            first_vector = vector
            ensure_collection(len(vector))
        points.append(
            PointStruct(
                id=str(uuid4()),
                vector=vector,
                payload={
                    "user_id": user_id,
                    "document_id": document_id,
                    "filename": filename,
                    "chunk_index": idx,
                    "text": chunk,
                },
            )
        )
    if points:
        client.upsert(collection_name=settings.RAG_COLLECTION, points=points)
    return len(points)


def search_context(user_id: int, query: str, limit: int = 5) -> list[str]:
    query_vector = embed(query)
    if not query_vector:
        return []
    ensure_collection(len(query_vector))
    hits = client.search(
        collection_name=settings.RAG_COLLECTION,
        query_vector=query_vector,
        query_filter=Filter(
            must=[FieldCondition(key="user_id", match=MatchValue(value=user_id))]
        ),
        limit=limit,
    )
    return [hit.payload.get("text", "") for hit in hits if hit.payload]


def inject_rag(messages: list, user_id: int) -> tuple[list, int]:
    latest_user = next((m.content for m in reversed(messages) if m.role == "user"), "")
    if not latest_user:
        return messages, 0
    chunks = search_context(user_id, latest_user)
    if not chunks:
        return messages, 0

    class Msg:
        def __init__(self, role, content):
            self.role = role
            self.content = content

    context = "\n\n".join([f"[RAG Chunk {i + 1}]\n{c}" for i, c in enumerate(chunks)])
    rag_msg = Msg(
        "system",
        "Use this private document context when useful. If it is not relevant, ignore it.\n\n" + context,
    )
    return [rag_msg] + messages, len(chunks)
