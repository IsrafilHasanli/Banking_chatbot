from app.core.db.database import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Date
from datetime import date


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    cognito_id: Mapped[str] = mapped_column(String(255), unique=True)
    email: Mapped[str] = mapped_column(String, unique=True)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    firstname: Mapped[str] = mapped_column(String(50))
    surname: Mapped[str] = mapped_column(String(50))
    birth_date: Mapped[date] = mapped_column(Date)
    signup_date: Mapped[date] = mapped_column(Date)
    phone_number: Mapped[str] = mapped_column(String(20))
