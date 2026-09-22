import random
from datetime import UTC, datetime

from app.models.product_model import BankAccount
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession


def generate_account_number(length: int = 16) -> str:
    return "".join(str(random.randint(0, 9)) for _ in range(length))


async def account_create(owner_id: int, account_type: str, currency: str, db: AsyncSession):
    new_account = BankAccount(
        owner_id=owner_id,
        account_type=account_type,
        account_number=generate_account_number(),
        currency=currency,
        creation_date=datetime.now(UTC),
        status="ACTIVE",
    )
    db.add(new_account)
    try:
        await db.commit()
        await db.refresh(new_account)
    except Exception as exc:
        await db.rollback()
        raise HTTPException(500, detail="Could not create account") from exc
    return new_account

