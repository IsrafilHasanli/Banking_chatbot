import base64
import hashlib
import hmac
import os
import uuid
from datetime import UTC, date, datetime, timedelta

from app.core.aws_boto3 import client_cognito
from app.core.config import settings
from app.models.user import User
from fastapi import HTTPException
from fastapi.concurrency import run_in_threadpool
from jose import jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


PASSWORD_HASH_ALGORITHM = "pbkdf2_sha256"
PASSWORD_HASH_ITERATIONS = 210_000


def _is_aws_auth() -> bool:
    return settings.AUTH_PROVIDER == "aws"


def _public_user(user: User) -> dict:
    return {
        "id": user.id,
        "cognito_id": user.cognito_id,
        "email": user.email,
        "firstname": user.firstname,
        "surname": user.surname,
        "birth_date": user.birth_date,
        "signup_date": user.signup_date,
        "phone_number": user.phone_number,
    }


def _hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        PASSWORD_HASH_ITERATIONS,
    )
    return "$".join(
        [
            PASSWORD_HASH_ALGORITHM,
            str(PASSWORD_HASH_ITERATIONS),
            base64.b64encode(salt).decode("ascii"),
            base64.b64encode(digest).decode("ascii"),
        ]
    )


def _verify_password(password: str, password_hash: str | None) -> bool:
    if not password_hash:
        return False

    try:
        algorithm, iterations, salt, expected_digest = password_hash.split("$", 3)
        if algorithm != PASSWORD_HASH_ALGORITHM:
            return False

        digest = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            base64.b64decode(salt),
            int(iterations),
        )
        return hmac.compare_digest(
            base64.b64encode(digest).decode("ascii"),
            expected_digest,
        )
    except (ValueError, TypeError):
        return False


def _create_token(subject: str, token_type: str, expires_delta: timedelta) -> str:
    expires_at = datetime.now(UTC) + expires_delta
    payload = {
        "sub": subject,
        "type": token_type,
        "exp": int(expires_at.timestamp()),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def _create_auth_tokens(user: User) -> dict:
    return {
        "access_token": _create_token(
            user.cognito_id,
            "access",
            timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        ),
        "refresh_token": _create_token(
            user.cognito_id,
            "refresh",
            timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        ),
        "token_type": "bearer",
    }


async def signup(
        email: str,
        password: str,
        firstname: str,
        surname: str,
        birth_date: date,
        phone_number: str,
        db: AsyncSession
):
    if _is_aws_auth():
        return await _signup_with_aws(
            email,
            password,
            firstname,
            surname,
            birth_date,
            phone_number,
            db,
        )

    return await _signup_with_postgres(
        email,
        password,
        firstname,
        surname,
        birth_date,
        phone_number,
        db,
    )


async def _signup_with_aws(
        email: str,
        password: str,
        firstname: str,
        surname: str,
        birth_date: date,
        phone_number: str,
        db: AsyncSession
):
    def _signup():
        return client_cognito.sign_up(
            ClientId=settings.AWS_CLIENT_ID,
            Username=email,
            Password=password,
            UserAttributes=[
                {"Name": "email", "Value": email}
            ]
        )

    try:
        response = await run_in_threadpool(_signup)
    except Exception as exc:
        raise HTTPException(status_code=502, detail="AWS Cognito signup failed") from exc

    newuser = User(
        cognito_id=response["UserSub"],
        email=email,
        firstname=firstname,
        surname=surname,
        birth_date=birth_date,
        signup_date=datetime.now(UTC),
        phone_number=phone_number,
        password_hash=None,
    )
    return await _save_user(newuser, db)


async def _signup_with_postgres(
        email: str,
        password: str,
        firstname: str,
        surname: str,
        birth_date: date,
        phone_number: str,
        db: AsyncSession
):
    existing_user = await db.execute(select(User).where(User.email == email))
    if existing_user.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="User with this email already exists")

    newuser = User(
        cognito_id=str(uuid.uuid4()),
        email=email,
        firstname=firstname,
        surname=surname,
        birth_date=birth_date,
        signup_date=datetime.now(UTC),
        phone_number=phone_number,
        password_hash=_hash_password(password),
    )
    return await _save_user(newuser, db)


async def _save_user(user: User, db: AsyncSession):
    db.add(user)

    try:
        await db.commit()
        await db.refresh(user)
    except Exception as exc:
        await db.rollback()
        raise HTTPException(500, detail="Could not save user") from exc

    return _public_user(user)


async def login(email: str, password: str, db: AsyncSession | None = None):
    if _is_aws_auth():
        def _login():
            return client_cognito.initiate_auth(
                ClientId=settings.AWS_CLIENT_ID,
                AuthFlow="USER_PASSWORD_AUTH",
                AuthParameters={
                    "USERNAME": email,
                    "PASSWORD": password
                }
            )

        response = await run_in_threadpool(_login)
        return response["AuthenticationResult"]

    if db is None:
        raise HTTPException(status_code=500, detail="DB session is required for Postgre auth")

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user or not _verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return _create_auth_tokens(user)


async def confirm(email: str, code: str):
    if not _is_aws_auth():
        return {"message": "Postgre auth mode does not require confirmation"}

    def _confirm():
        return client_cognito.confirm_sign_up(
            ClientId=settings.AWS_CLIENT_ID,
            Username=email,
            ConfirmationCode=code
        )

    return await run_in_threadpool(_confirm)
