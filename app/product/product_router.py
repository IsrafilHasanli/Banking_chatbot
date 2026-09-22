from app.auth.security import get_current_user
from app.core.db.deps import get_db
from app.models.user import User
from app.product.product_service import account_create
from app.schemas.product_schema import BankAccount
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/product")


@router.post("/create-account")
async def create_account(
    account: BankAccount,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await account_create(
        owner_id=user.id,
        account_type=account.account_type,
        currency=account.currency,
        db=db,
    )
