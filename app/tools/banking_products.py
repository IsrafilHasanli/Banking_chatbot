from app.services.banking_product_service import (
    block_account_for_user,
    create_account_for_user,
    create_card_for_user,
    get_account_and_card_statuses_for_user,
)
from sqlalchemy.ext.asyncio import AsyncSession


async def create_customer_account(
    user_id: int,
    account_type: str,
    currency: str,
    db: AsyncSession,
) -> str:
    return await create_account_for_user(user_id, account_type, currency, db)


async def create_customer_card(
    user_id: int,
    card_type: str,
    linked_account_number: str,
    db: AsyncSession,
) -> str:
    return await create_card_for_user(user_id, card_type, linked_account_number, db)


async def block_customer_account(
    user_id: int,
    account_number: str,
    reason: str,
    db: AsyncSession,
) -> str:
    return await block_account_for_user(user_id, account_number, reason, db)


async def show_customer_product_statuses(
    user_id: int,
    query: str,
    db: AsyncSession,
) -> str:
    return await get_account_and_card_statuses_for_user(user_id, query, db)
