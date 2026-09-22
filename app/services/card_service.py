from app.services.banking_product_service import block_card_for_user
from sqlalchemy.ext.asyncio import AsyncSession


async def block_card(user_id: int, card_identifier: str, reason: str, db: AsyncSession) -> str:
    return await block_card_for_user(user_id, card_identifier, reason, db)
