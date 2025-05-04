from sqlalchemy import Integer, Float, ForeignKey
from sqlalchemy.orm import mapped_column, relationship

from database.db import Base


class Account(Base):
    """Таблица для счета"""

    __tablename__ = 'accounts'

    id = mapped_column(Integer, primary_key=True, index=True)
    total = mapped_column(Float, default=0)
    user_id = mapped_column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="account")