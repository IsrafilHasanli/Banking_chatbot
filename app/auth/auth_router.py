from app.auth.auth_service import signup, login, confirm
from app.schemas.user_schema import UserAuth, ConfirmRequest, UserReg
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.deps import get_db

router = APIRouter(prefix="/auth")


@router.post("/signup")
async def register(user: UserReg, db: AsyncSession = Depends(get_db)):
    try:
        return await signup(user.email, user.password, user.firstname, user.surname, user.birth_date, user.phone_number,
                            db)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login")
async def user_login(user: UserAuth, db: AsyncSession = Depends(get_db)):
    try:
        return await login(user.email, user.password, db)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/confirm")
async def user_confirm(user: ConfirmRequest):
    try:
        return await confirm(user.email, user.code)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))
