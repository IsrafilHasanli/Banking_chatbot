from pydantic import BaseModel
from datetime import date
class UserAuth(BaseModel):
    email: str
    password: str
class UserReg(BaseModel):
    email: str
    password: str
    firstname: str
    surname: str
    birth_date: date
    phone_number: str
class ConfirmRequest(BaseModel):
    email: str
    code: str


class ChatRequest(BaseModel):
    message: str
