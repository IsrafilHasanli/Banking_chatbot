from sqlalchemy.orm import Mapped, mapped_column
from app.core.db.database import Base
from sqlalchemy import Integer, String, Date,Float
from datetime import date

class BankAccount(Base):
    __tablename__ = "accounts"

    account_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    account_number: Mapped[str] = mapped_column(String(16), unique=True)
    owner_id: Mapped[int] = mapped_column(Integer)
    account_type: Mapped[str] = mapped_column(String(50))
    currency: Mapped[str] = mapped_column(String(50))
    balance: Mapped[float] = mapped_column(Float(20),default=0)
    creation_date: Mapped[date] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(50))
