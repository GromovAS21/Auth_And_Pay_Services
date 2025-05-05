from sqlalchemy import Integer, String, Boolean
from sqlalchemy.orm import mapped_column, relationship

from database.db import Base


class User(Base):
    """Таблица пользователя в БД"""

    __tablename__ = "users"

    id = mapped_column(Integer, primary_key=True, index=True)
    email = mapped_column(String, nullable=False, unique=True)
    username = mapped_column(String, nullable=False)
    first_name = mapped_column(String, nullable=False)
    last_name = mapped_column(String, nullable=False)
    password = mapped_column(String)
    is_active = mapped_column(Boolean, default=True)
    is_admin = mapped_column(Boolean, default=False)

    account = relationship("Account", back_populates="user")
    transaction = relationship("Transaction", back_populates="user")

