from pydantic import BaseModel

class BankAccount(BaseModel):

    account_type: str
    currency: str




