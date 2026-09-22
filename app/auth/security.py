import requests
from app.core.config import settings
from app.core.db.deps import get_db
from app.core.error_messages import AuthErrors
from app.models.user import User
from fastapi import Depends, HTTPException
from fastapi.concurrency import run_in_threadpool
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

security = HTTPBearer()


def _aws_issuer() -> str:
    return f"https://cognito-idp.{settings.AWS_REGION}.amazonaws.com/{settings.AWS_USER_POOL_ID}"


def _aws_jwks_url() -> str:
    return f"{_aws_issuer()}/.well-known/jwks.json"


def get_jwks():
    response = requests.get(_aws_jwks_url(), timeout=10)
    response.raise_for_status()
    return response.json()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    token = credentials.credentials

    if settings.AUTH_PROVIDER == "aws":
        return await _get_current_user_from_aws(token, db)

    return await _get_current_user_from_postgres(token, db)


async def _get_current_user_from_aws(token: str, db: AsyncSession):
    try:
        jwks = await run_in_threadpool(get_jwks)
        header = jwt.get_unverified_header(token)
        kid = header.get("kid")

        key = next((k for k in jwks["keys"] if k["kid"] == kid), None)
        if not key:
            raise HTTPException(status_code=401, detail=AuthErrors.PUBLIC_KEY_NOTFOUND)

        payload = jwt.decode(
            token,
            key,
            algorithms=["RS256"],
            issuer=_aws_issuer(),
        )

        token_use = payload.get("token_use")
        if token_use != "access":
            raise HTTPException(status_code=401, detail=AuthErrors.ACCESS_TOKEN_REQUIRED)

        user_sub = payload.get("sub")
        if not user_sub:
            raise HTTPException(status_code=401, detail=AuthErrors.INVALID_TOKEN_PAYLOAD)

        return await _get_user_by_auth_subject(user_sub, db)

    except JWTError:
        raise HTTPException(status_code=401, detail=AuthErrors.INVALID_JWT_TOKEN)


async def _get_current_user_from_postgres(token: str, db: AsyncSession):
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )

        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail=AuthErrors.ACCESS_TOKEN_REQUIRED)

        user_sub = payload.get("sub")
        if not user_sub:
            raise HTTPException(status_code=401, detail=AuthErrors.INVALID_TOKEN_PAYLOAD)

        return await _get_user_by_auth_subject(user_sub, db)

    except JWTError:
        raise HTTPException(status_code=401, detail=AuthErrors.INVALID_JWT_TOKEN)


async def _get_user_by_auth_subject(auth_subject: str, db: AsyncSession):
    result = await db.execute(
        select(User).where(User.cognito_id == auth_subject)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(404, AuthErrors.USER_NOTFOUND_DB)

    return user
