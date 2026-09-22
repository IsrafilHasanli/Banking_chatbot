from app.models.support_request import SupportRequest
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession


async def create_support_request(
    user_id: int,
    category: str,
    subject: str,
    description: str,
    priority: str,
    db: AsyncSession,
) -> SupportRequest:
    category_value = str(category or "GENERAL").strip().upper()[:50] or "GENERAL"
    subject_value = str(subject or "Support request").strip()[:120] or "Support request"
    description_value = str(description or "No description provided.").strip() or "No description provided."
    priority_value = str(priority or "NORMAL").strip().upper()[:30] or "NORMAL"
    support_request = SupportRequest(
        user_id=user_id,
        category=category_value,
        subject=subject_value,
        description=description_value,
        priority=priority_value,
        status="OPEN",
    )
    db.add(support_request)
    await db.commit()
    await db.refresh(support_request)
    return support_request


async def list_support_requests(user_id: int, db: AsyncSession, limit: int = 5) -> list[SupportRequest]:
    result = await db.execute(
        select(SupportRequest)
        .where(SupportRequest.user_id == user_id)
        .order_by(desc(SupportRequest.created_at))
        .limit(limit)
    )
    return list(result.scalars().all())
