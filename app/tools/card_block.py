from app.services.card_service import block_card
from sqlalchemy.ext.asyncio import AsyncSession


async def block_customer_card(
    user_id: int,
    card_identifier: str,
    reason: str,
    db: AsyncSession,
) -> str:
    return await block_card(user_id, card_identifier, reason, db)
