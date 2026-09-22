import hashlib
import re
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from app.core.config import settings
from app.models.chat_cache import ChatCache
from fastapi.concurrency import run_in_threadpool
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession


SEMANTIC_CACHE_COLLECTION = "chat_semantic_cache"
VECTOR_SIZE = 384

NON_CACHEABLE_PATTERNS = (
    "balance",
    "balans",
    "account",
    "hesab",
    "block",
    "blocked",
    "blok",
    "bloklu",
    "bloklan",
    "freeze",
    "create",
    "open",
    "order",
    "issue",
    "new card",
    "create card",
    "order card",
    "issue card",
    "kart yarat",
    "kart sifariş",
    "lost",
    "stolen",
    "support",
    "request",
    "ticket",
    "status",
    "transfer",
    "köçür",
    "kocur",
    "send",
    "pay",
    "payment",
    "ödəniş",
    "odenis",
    "money",
    "pul",
    "azn",
    "current",
    "how much",
    "my ",
    "mənim",
    "menim",
)

FAQ_CACHEABLE_PATTERNS = (
    "faq",
    "bank",
    "banking",
    "policy",
    "rule",
    "rules",
    "terms",
    "condition",
    "conditions",
    "tariff",
    "tarif",
    "fee",
    "fees",
    "commission",
    "limit",
    "interest",
    "faiz",
    "loan",
    "credit",
    "kredit",
    "deposit",
    "depozit",
    "card",
    "kart",
    "cashback",
    "service",
    "xidmət",
    "xidmet",
    "qayda",
    "şərt",
    "sert",
)


def normalize_prompt(prompt: str) -> str:
    return re.sub(r"\s+", " ", prompt.strip().lower())


def is_cacheable_prompt(prompt: str) -> bool:
    normalized = normalize_prompt(prompt)
    if len(normalized) < 8:
        return False
    if any(pattern in normalized for pattern in NON_CACHEABLE_PATTERNS):
        return False

    return any(pattern in normalized for pattern in FAQ_CACHEABLE_PATTERNS)


def make_cache_key(user_id: int, prompt: str) -> str:
    source = f"{user_id}:{normalize_prompt(prompt)}"
    return hashlib.sha256(source.encode("utf-8")).hexdigest()


def _timestamp(value: datetime) -> int:
    return int(value.timestamp())


def _get_cache_vector(prompt: str) -> list[float]:
    from app.rag.rag import get_model

    return get_model().encode(normalize_prompt(prompt)).tolist()


def _ensure_semantic_cache_collection() -> None:
    from app.core.db.qdrant_db import client
    from qdrant_client.http.models import Distance, VectorParams

    if not client.collection_exists(SEMANTIC_CACHE_COLLECTION):
        client.create_collection(
            collection_name=SEMANTIC_CACHE_COLLECTION,
            vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
        )


def _search_semantic_cache(user_id: int, prompt: str) -> str | None:
    if not settings.CHAT_SEMANTIC_CACHE_ENABLED:
        return None

    from app.core.db.qdrant_db import client
    from qdrant_client.http.models import FieldCondition, Filter, MatchValue, Range

    _ensure_semantic_cache_collection()
    results = client.search(
        collection_name=SEMANTIC_CACHE_COLLECTION,
        query_vector=_get_cache_vector(prompt),
        query_filter=Filter(
            must=[
                FieldCondition(key="user_id", match=MatchValue(value=user_id)),
                FieldCondition(key="expires_at_ts", range=Range(gt=_timestamp(datetime.now(UTC)))),
            ]
        ),
        limit=1,
        score_threshold=settings.CHAT_SEMANTIC_CACHE_THRESHOLD,
    )
    if not results:
        return None

    return results[0].payload.get("response")


def _upsert_semantic_cache(user_id: int, prompt: str, response: str, expires_at: datetime) -> None:
    if not settings.CHAT_SEMANTIC_CACHE_ENABLED:
        return

    from app.core.db.qdrant_db import client

    _ensure_semantic_cache_collection()
    now = datetime.now(UTC)
    client.upsert(
        collection_name=SEMANTIC_CACHE_COLLECTION,
        points=[
            {
                "id": str(uuid4()),
                "vector": _get_cache_vector(prompt),
                "payload": {
                    "user_id": user_id,
                    "prompt": prompt,
                    "normalized_prompt": normalize_prompt(prompt),
                    "response": response,
                    "created_at": now.isoformat(),
                    "expires_at": expires_at.isoformat(),
                    "expires_at_ts": _timestamp(expires_at),
                },
            }
        ],
    )


async def get_cached_response(user_id: int, prompt: str, db: AsyncSession) -> str | None:
    if not settings.CHAT_CACHE_ENABLED or not is_cacheable_prompt(prompt):
        return None

    now = datetime.now(UTC)
    cache_key = make_cache_key(user_id, prompt)
    result = await db.execute(
        select(ChatCache).where(
            ChatCache.cache_key == cache_key,
            ChatCache.expires_at > now,
        )
    )
    cached = result.scalar_one_or_none()
    if cached:
        return cached.response

    return await run_in_threadpool(_search_semantic_cache, user_id, prompt)


async def set_cached_response(user_id: int, prompt: str, response: str, db: AsyncSession) -> None:
    if not settings.CHAT_CACHE_ENABLED or not is_cacheable_prompt(prompt):
        return

    now = datetime.now(UTC)
    cache_key = make_cache_key(user_id, prompt)
    expires_at = now + timedelta(seconds=settings.CHAT_CACHE_TTL_SECONDS)

    result = await db.execute(select(ChatCache).where(ChatCache.cache_key == cache_key))
    cached = result.scalar_one_or_none()

    if cached:
        cached.response = response
        cached.created_at = now
        cached.expires_at = expires_at
    else:
        db.add(
            ChatCache(
                cache_key=cache_key,
                user_id=user_id,
                prompt=prompt,
                response=response,
                created_at=now,
                expires_at=expires_at,
            )
        )

    await db.commit()
    await run_in_threadpool(_upsert_semantic_cache, user_id, prompt, response, expires_at)


async def cleanup_expired_cache(db: AsyncSession) -> None:
    await db.execute(delete(ChatCache).where(ChatCache.expires_at <= datetime.now(UTC)))
    await db.commit()
