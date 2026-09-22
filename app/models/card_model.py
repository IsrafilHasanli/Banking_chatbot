from datetime import UTC, date, datetime

from app.core.db.database import Base
from sqlalchemy import Date, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column


class BankCard(Base):
    __tablename__ = "cards"

    card_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    owner_id: Mapped[int] = mapped_column(Integer, index=True)
    card_number: Mapped[str] = mapped_column(String(19), unique=True, index=True)
    card_type: Mapped[str] = mapped_column(String(50), default="DEBIT")
    linked_account_number: Mapped[str | None] = mapped_column(String(16), nullable=True)
    expiry_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="ACTIVE")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )
    blocked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
