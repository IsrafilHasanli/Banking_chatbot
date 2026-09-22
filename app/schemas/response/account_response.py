from pydantic import BaseModel,ConfigDict

class AccountResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)  # 🔥 BU MÜTLƏQDİR

    account_number: str
    balance: float
    currency: str
    owner_id: int