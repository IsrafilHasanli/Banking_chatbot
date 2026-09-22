from app.services.support_request_service import create_support_request, list_support_requests
from sqlalchemy.ext.asyncio import AsyncSession


async def create_support_ticket(
    user_id: int,
    category: str,
    subject: str,
    description: str,
    priority: str,
    db: AsyncSession,
) -> str:
    support_request = await create_support_request(
        user_id=user_id,
        category=category,
        subject=subject,
        description=description,
        priority=priority,
        db=db,
    )
    return (
        f"Support request #{support_request.request_id} was created. "
        f"Status: {support_request.status}. Priority: {support_request.priority}."
    )


async def show_support_tickets(user_id: int, db: AsyncSession) -> str:
    requests = await list_support_requests(user_id, db)
    if not requests:
        return "You do not have any support requests yet."

    lines = ["Your latest support requests:"]
    for item in requests:
        lines.append(
            f"#{item.request_id} - {item.subject} | {item.status} | {item.priority} | {item.created_at:%Y-%m-%d}"
        )
    return "\n".join(lines)
