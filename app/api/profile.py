from fastapi import APIRouter, Depends
from app.auth.security import get_current_user
from app.models.user import User


router = APIRouter(prefix="/Profile")

@router.get("/")
async def profile(user: User = Depends(get_current_user)):
    return user