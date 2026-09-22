from langchain.tools import tool
from app.tools.check_balance import check_balance
from app.rag.rag import retrieve
from sqlalchemy.ext.asyncio import AsyncSession
from app.tools.money_transfer import money_transfer
from app.tools.card_block import block_customer_card
from app.tools.banking_products import (
    block_customer_account,
    create_customer_account,
    create_customer_card,
    show_customer_product_statuses,
)
from app.tools.support_requests import create_support_ticket, show_support_tickets
def make_check_balance_tool(user_id,db: AsyncSession):

    @tool
    async def check_balance_tool(query: str) -> str:
        """
        Use this tool when user asks about:
        - account balance
        - how much money they have
        - current balance
        show each account seperately with its account number, currency and amount.
        """
        return await check_balance(user_id, db)

    return check_balance_tool

def make_rag_tool():

    @tool
    async def rag_search(query: str) -> str:
        """
                Search banking knowledge base.

                Use this tool for:
                - general banking questions
                - policies
                - interest rates
        - FAQs
                """
        try:
            docs = retrieve(query)
        except ImportError:
            return "Knowledge base search is not available in this Docker image."

        context = "\n\n".join(docs)

        return f"""
    Use the following context to answer:

    {context}

    Question: {query}
    """

    return rag_search


def make_transfer_money(user_id,db: AsyncSession):

    @tool
    async def transfer_money_tool(
            from_account: str,
            to_account: str,
            amount: float
    ) -> str:
        """
        Transfer money from one account to another.

        Inputs:
        - from_account: sender account number
        - to_account: receiver account number
        - amount: amount to transfer
        """
        result = await money_transfer(
            user_id,
            from_account,
            to_account,
            amount,
            db
        )
        return str(result)

    return transfer_money_tool

def make_block_card_tool(user_id, db: AsyncSession):

    @tool
    async def block_card_tool(
            card_identifier: str = "",
            reason: str = ""
    ) -> str:
        """
        Block a customer's bank card.

        Use this tool when the user wants to:
        - block a card
        - freeze a card
        - report a lost or stolen card

        Inputs:
        - card_identifier: full card number or last digits. Ask the user if missing.
        - reason: why the card should be blocked, such as lost, stolen, fraud, or user request.
        """
        return await block_customer_card(user_id, card_identifier, reason, db)

    return block_card_tool


def make_block_account_tool(user_id, db: AsyncSession):

    @tool
    async def block_account_tool(
            account_number: str = "",
            reason: str = ""
    ) -> str:
        """
        Block a customer's bank account.

        Use this tool when the user wants to:
        - block an account
        - freeze an account
        - stop activity on an account

        Inputs:
        - account_number: account number to block. Ask the user if missing.
        - reason: why the account should be blocked.
        """
        return await block_customer_account(user_id, account_number, reason, db)

    return block_account_tool


def make_create_account_tool(user_id, db: AsyncSession):

    @tool
    async def create_account_tool(
            account_type: str = "CURRENT",
            currency: str = "AZN"
    ) -> str:
        """
        Create a new bank account for the current user.

        Use this tool when the user wants to:
        - create an account
        - open a current account
        - open a savings account

        Inputs:
        - account_type: CURRENT or SAVINGS.
        - currency: AZN, USD, or EUR.
        """
        return await create_customer_account(user_id, account_type, currency, db)

    return create_account_tool


def make_create_card_tool(user_id, db: AsyncSession):

    @tool
    async def create_card_tool(
            card_type: str = "DEBIT",
            linked_account_number: str = ""
    ) -> str:
        """
        Create a new bank card for the current user.

        Use this tool when the user wants to:
        - create a card
        - order a debit card
        - order a credit card

        Inputs:
        - card_type: DEBIT or CREDIT.
        - linked_account_number: account number to link. Ask the user if multiple accounts exist.
        """
        return await create_customer_card(user_id, card_type, linked_account_number, db)

    return create_card_tool


def make_show_product_statuses_tool(user_id, db: AsyncSession):

    @tool
    async def show_product_statuses_tool(query: str = "") -> str:
        """
        Show the current user's account and card status, including whether each item is blocked.

        Use this tool when the user asks to:
        - check whether an account is blocked
        - check whether a card is blocked
        - show account status
        - show card status
        - list accounts or cards with blocked/not blocked status

        Inputs:
        - query: the user's original question. Include card/account number digits if provided.
        """
        return await show_customer_product_statuses(user_id, query, db)

    return show_product_statuses_tool


def make_create_support_request_tool(user_id, db: AsyncSession):

    @tool
    async def create_support_request_tool(
            category: str = "GENERAL",
            subject: str = "Support request",
            description: str = "",
            priority: str = "NORMAL"
    ) -> str:
        """
        Create a support request for the current user.

        Use this tool when the user asks to:
        - create a support request
        - open a ticket
        - report a banking issue
        - contact support through the bot

        Inputs:
        - category: CARD, ACCOUNT, TRANSFER, LOGIN, GENERAL, or similar.
        - subject: short title of the issue.
        - description: details from the user. Ask a short follow-up if missing.
        - priority: LOW, NORMAL, HIGH, or URGENT.
        """
        if not str(description or "").strip():
            return "Please describe the issue you want support to help with."

        return await create_support_ticket(
            user_id,
            category,
            subject,
            description,
            priority,
            db
        )

    return create_support_request_tool


def make_show_support_requests_tool(user_id, db: AsyncSession):

    @tool
    async def show_support_requests_tool(query: str = "") -> str:
        """
        Show the user's latest support requests and their statuses.

        Use this tool when the user asks to:
        - show my support requests
        - list my tickets
        - check support request status
        """
        return await show_support_tickets(user_id, db)

    return show_support_requests_tool
