from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.product_model import BankAccount

async def check_balance(user_id: int, db: AsyncSession):
    """to check balance of customer"""

    result = await db.execute(
        select(BankAccount).where(BankAccount.owner_id == user_id)
    )
    accounts = result.scalars().all()

    if not accounts:
        return "You have no accounts."

    response = ""
    for acc in accounts:
        status = str(acc.status or "UNKNOWN").upper()
        blocked_note = "blocked" if status == "BLOCKED" else "not blocked"
        response += (
            f"Account {acc.account_number}: {acc.balance} {acc.currency} | "
            f"Status: {status} ({blocked_note})\n"
        )

    return response
