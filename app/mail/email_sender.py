import asyncio
import json
import logging
from typing import Optional

from app.core.aws_boto3 import client_lambda
from app.core.config import settings
from app.models.user import User
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

SMTP_SERVER = settings.SMTP_SERVER
MAIL_USER = settings.MAIL_USER
MAIL_PASS = settings.MAIL_PASS

async def send_email(
    subject: str,
    body: str,
    to_email: str | None = None,
    user_id: int | None = None,
    db: Optional[AsyncSession] = None,
):
    if not to_email and not user_id:
        raise ValueError("Provide email address or User ID")
    email = to_email
    if user_id and not to_email:
        if not db:
            raise ValueError("DB session required when using user_id")
        email = await get_email_by_id(user_id, db)

    response = await asyncio.to_thread(
        client_lambda.invoke,
        FunctionName="Email_send_universal",
        InvocationType="Event",
        Payload=json.dumps({
            "smtp_server": SMTP_SERVER,
            "mail_user": MAIL_USER,
            "mail_pass": MAIL_PASS,
            "to_email": email,
            "subject": subject,
            "body": body,
        }),
    )

    result = json.load(response["Payload"])
    logger.info("Queued email delivery through Lambda for user_id=%s", user_id)
    return result


async def get_email_by_id(user_id,db):
    query_result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user_result = query_result.scalars().first()
    if not user_result:
        raise ValueError("User not found")
    return user_result.email
