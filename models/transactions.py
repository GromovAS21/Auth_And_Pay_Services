from sqlalchemy import Integer, ForeignKey, Float, String
from sqlalchemy.orm import mapped_column, relationship

from database.db import Base


class Transaction(Base):
    """Таблица платежей"""

    __tablename__ = 'transactions'

    id = mapped_column(Integer, primary_key=True, index=True)
    transaction_id = mapped_column(String, unique=True, index=True)
    account_id = mapped_column(Integer, ForeignKey('accounts.id'))
    user_id = mapped_column(Integer, ForeignKey('users.id'))
    amount = mapped_column(Float)

    account = relationship('Account', back_populates='transaction')
    user = relationship('User', back_populates='transaction')