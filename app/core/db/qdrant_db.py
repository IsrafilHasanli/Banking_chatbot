from app.core.config import settings
from qdrant_client import QdrantClient


if not settings.QDRANT_URL:
    raise RuntimeError("QDRANT_URL is required to use vector search or semantic cache")

client = QdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY)
