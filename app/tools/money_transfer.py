from sqlalchemy import select
from app.models.product_model import BankAccount
import asyncio
from app.mail.templates.balance_template import balance_update_template
from app.mail.email_sender import send_email
async def money_transfer(user_id, account_number, to_account, amount, db):

    result_sender = await db.execute(
        select(BankAccount)
        .where(BankAccount.owner_id == user_id)
        .where(BankAccount.account_number == account_number)
    )

    result_receiver = await db.execute(
        select(BankAccount)
        .where(BankAccount.account_number == to_account)
    )

    account_sender = result_sender.scalars().first()
    account_receiver = result_receiver.scalars().first()

    if not account_sender:
        return "sender not found"
    if not account_receiver:
        return "receiver not found"
    if amount <= 0:
        return "invalid amount"
    if amount > account_sender.balance:
        return "insufficient balance"

    account_sender.balance -= amount
    account_receiver.balance += amount
    sender_mail_template = balance_update_template(
        amount,
        account_sender.currency,
        account_sender.balance,
        account_sender.account_number,
        "DEBIT"
    )
    receiver_mail_template = balance_update_template(
        amount,
        account_receiver.currency,
        account_receiver.balance,
        account_receiver.account_number,
        "CREDIT"
    )

    await db.commit()
    asyncio.create_task(
        send_email(
            subject=sender_mail_template["subject"],
            body=sender_mail_template["body"],
            user_id=account_sender.owner_id,
            db=db
        )
    )

    # receiver email
    asyncio.create_task(
        send_email(
            subject=receiver_mail_template["subject"],
            body=receiver_mail_template["body"],
            user_id=account_receiver.owner_id,
            db=db
        )
    )

    return account_sender
