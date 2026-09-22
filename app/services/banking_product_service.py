from datetime import UTC, date, datetime
import random
import re

from app.models.card_model import BankCard
from app.models.product_model import BankAccount
from app.services.support_request_service import create_support_request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


SUPPORTED_ACCOUNT_TYPES = {"CURRENT", "SAVINGS"}
SUPPORTED_CARD_TYPES = {"DEBIT", "CREDIT"}
SUPPORTED_CURRENCIES = {"AZN", "USD", "EUR"}


def _normalize_choice(value: str | None, fallback: str, allowed: set[str]) -> str:
    normalized = str(value or fallback).strip().upper()
    return normalized if normalized in allowed else fallback


def _digits(value: str | None) -> str:
    return re.sub(r"\D", "", str(value or ""))


def _mask_card(card_number: str) -> str:
    digits = _digits(card_number)
    if len(digits) < 4:
        return "selected card"
    return f"**** **** **** {digits[-4:]}"


def _status_note(status: str | None) -> str:
    normalized = str(status or "UNKNOWN").upper()
    blocked_note = "blocked" if normalized == "BLOCKED" else "not blocked"
    return f"{normalized} ({blocked_note})"


async def _generate_unique_account_number(db: AsyncSession) -> str:
    for _ in range(10):
        account_number = "".join(str(random.randint(0, 9)) for _ in range(16))
        result = await db.execute(
            select(BankAccount.account_id).where(BankAccount.account_number == account_number)
        )
        if result.scalar_one_or_none() is None:
            return account_number
    raise RuntimeError("Could not generate a unique account number.")


async def _generate_unique_card_number(db: AsyncSession) -> str:
    for _ in range(10):
        card_number = "4" + "".join(str(random.randint(0, 9)) for _ in range(15))
        result = await db.execute(select(BankCard.card_id).where(BankCard.card_number == card_number))
        if result.scalar_one_or_none() is None:
            return card_number
    raise RuntimeError("Could not generate a unique card number.")


async def create_account_for_user(
    user_id: int,
    account_type: str,
    currency: str,
    db: AsyncSession,
) -> str:
    account_type_value = _normalize_choice(account_type, "CURRENT", SUPPORTED_ACCOUNT_TYPES)
    currency_value = _normalize_choice(currency, "AZN", SUPPORTED_CURRENCIES)

    account = BankAccount(
        owner_id=user_id,
        account_type=account_type_value,
        account_number=await _generate_unique_account_number(db),
        currency=currency_value,
        balance=0,
        creation_date=date.today(),
        status="ACTIVE",
    )
    db.add(account)
    await db.commit()
    await db.refresh(account)

    return (
        f"{account_type_value.title()} account created. "
        f"Account number: {account.account_number}. Currency: {account.currency}. "
        f"Status: {_status_note(account.status)}."
    )


async def create_card_for_user(
    user_id: int,
    card_type: str,
    linked_account_number: str,
    db: AsyncSession,
) -> str:
    card_type_value = _normalize_choice(card_type, "DEBIT", SUPPORTED_CARD_TYPES)
    account_number = _digits(linked_account_number)

    if not account_number:
        result = await db.execute(
            select(BankAccount).where(
                BankAccount.owner_id == user_id,
                BankAccount.status == "ACTIVE",
            )
        )
        active_accounts = list(result.scalars().all())
        if len(active_accounts) == 1:
            account = active_accounts[0]
        elif not active_accounts:
            return "Please create an active account before requesting a card."
        else:
            return "Please provide the account number you want to link the card to."
    else:
        result = await db.execute(
            select(BankAccount).where(
                BankAccount.owner_id == user_id,
                BankAccount.account_number == account_number,
            )
        )
        account = result.scalar_one_or_none()
        if account is None:
            return "I could not find that account in your profile."
        if account.status != "ACTIVE":
            return "That account is not active, so I cannot create a card for it."

    card = BankCard(
        owner_id=user_id,
        card_number=await _generate_unique_card_number(db),
        card_type=card_type_value,
        linked_account_number=account.account_number,
        expiry_date=date(date.today().year + 4, date.today().month, 1),
        status="ACTIVE",
    )
    db.add(card)
    await db.commit()
    await db.refresh(card)

    return (
        f"{card.card_type.title()} card created and linked to account {account.account_number}. "
        f"Card: {_mask_card(card.card_number)}. Status: {_status_note(card.status)}."
    )


async def get_account_and_card_statuses_for_user(
    user_id: int,
    query: str,
    db: AsyncSession,
) -> str:
    query_text = str(query or "").lower()
    digits = _digits(query)
    wants_cards = any(word in query_text for word in ("card", "kart"))
    wants_accounts = any(word in query_text for word in ("account", "hesab"))
    show_accounts = wants_accounts or not wants_cards
    show_cards = wants_cards or not wants_accounts

    lines: list[str] = []

    if show_accounts:
        account_stmt = select(BankAccount).where(BankAccount.owner_id == user_id)
        if digits:
            account_stmt = account_stmt.where(BankAccount.account_number.endswith(digits))
        account_result = await db.execute(account_stmt)
        accounts = list(account_result.scalars().all())
        if accounts:
            lines.append("Accounts:")
            for account in accounts:
                lines.append(
                    f"- {account.account_number} | {account.account_type} | "
                    f"{account.currency} | Status: {_status_note(account.status)}"
                )
        elif wants_accounts or digits:
            lines.append("No matching accounts found in your profile.")

    if show_cards:
        card_result = await db.execute(select(BankCard).where(BankCard.owner_id == user_id))
        cards = list(card_result.scalars().all())
        if digits:
            cards = [
                card
                for card in cards
                if _digits(card.card_number) == digits or _digits(card.card_number).endswith(digits)
            ]

        if cards:
            lines.append("Cards:")
            for card in cards:
                blocked_at = f" | Blocked at: {card.blocked_at:%Y-%m-%d %H:%M}" if card.blocked_at else ""
                linked_account = card.linked_account_number or "not linked"
                lines.append(
                    f"- {_mask_card(card.card_number)} | {card.card_type} | "
                    f"Linked account: {linked_account} | Status: {_status_note(card.status)}"
                    f"{blocked_at}"
                )
        elif wants_cards or digits:
            lines.append("No matching cards found in your profile.")

    if not lines:
        return "You do not have any accounts or cards yet."

    return "\n".join(lines)


async def block_account_for_user(
    user_id: int,
    account_number: str,
    reason: str,
    db: AsyncSession,
) -> str:
    normalized_account = _digits(account_number)
    if not normalized_account:
        return "Please provide the account number you want to block."

    result = await db.execute(
        select(BankAccount).where(
            BankAccount.owner_id == user_id,
            BankAccount.account_number == normalized_account,
        )
    )
    account = result.scalar_one_or_none()
    if account is None:
        return "I could not find that account in your profile."
    if account.status == "BLOCKED":
        return f"Account {account.account_number} is already blocked."

    account.status = "BLOCKED"
    request = await create_support_request(
        user_id=user_id,
        category="ACCOUNT",
        subject=f"Account blocked {account.account_number}",
        description=f"Account was blocked by chatbot request. Reason: {reason or 'Not provided'}",
        priority="URGENT",
        db=db,
    )
    return f"Account {account.account_number} has been blocked. Support request #{request.request_id} was created."


async def block_card_for_user(
    user_id: int,
    card_identifier: str,
    reason: str,
    db: AsyncSession,
) -> str:
    digits = _digits(card_identifier)
    if not digits:
        return "Please provide the card number or the last 4 digits of the card you want to block."

    result = await db.execute(select(BankCard).where(BankCard.owner_id == user_id))
    cards = list(result.scalars().all())
    matching_cards = [
        card
        for card in cards
        if _digits(card.card_number) == digits or _digits(card.card_number).endswith(digits)
    ]

    if len(matching_cards) > 1:
        return "I found more than one matching card. Please provide the full card number or more digits."

    if not matching_cards:
        request = await create_support_request(
            user_id=user_id,
            category="CARD",
            subject="Card block request",
            description=(
                f"Customer requested card blocking for identifier ending '{digits[-4:]}'. "
                f"Reason: {reason or 'Not provided'}"
            ),
            priority="URGENT",
            db=db,
        )
        return (
            "I could not find that card in your profile, so I created an urgent support request "
            f"#{request.request_id} for manual card blocking."
        )

    card = matching_cards[0]
    if card.status == "BLOCKED":
        return f"{_mask_card(card.card_number)} is already blocked."

    card.status = "BLOCKED"
    card.blocked_at = datetime.now(UTC)
    request = await create_support_request(
        user_id=user_id,
        category="CARD",
        subject=f"Card blocked {_mask_card(card.card_number)}",
        description=f"Card was blocked by chatbot request. Reason: {reason or 'Not provided'}",
        priority="URGENT",
        db=db,
    )
    return f"{_mask_card(card.card_number)} has been blocked. Support request #{request.request_id} was created."
