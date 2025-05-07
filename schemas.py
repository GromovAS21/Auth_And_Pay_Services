from typing import List

from pydantic import BaseModel, EmailStr, Field


class CreateUserSchema(BaseModel):
    """Схема для создания пользователя."""

    email: EmailStr = Field(..., description="Email пользователя")
    username: str = Field(..., min_length=2, max_length=50, description="Логин пользователя")
    first_name: str = Field(..., min_length=2, max_length=50, description="Имя пользователя")
    last_name: str = Field(..., min_length=2, max_length=50, description="Фамилия пользователя")
    password: str = Field(..., min_length=8, description="Пароль")


class UpdateUserSchema(CreateUserSchema):
    """Схема для обновления пользователя."""

    password: None = Field(None, exclude=True)
    is_active: bool = Field(default=True, description="Активный статус пользователя")
    is_admin: bool = Field(default=False, description="Админ статус пользователя")


class UserSchema(BaseModel):
    """Схема для получения пользователя."""

    id: int = Field(..., description="ID пользователя")
    email: EmailStr = Field(..., description="Email пользователя")
    full_name: str = Field(..., description="ФИО пользователя")

class AccountSchema(BaseModel):
    """Схема для получения счетов пользователя."""
    id: int = Field(..., description="ID аккаунта")
    total: float = Field(..., description="Баланс пользователя")

class TransactionSchema(BaseModel):
    """Схема для получения транзакции пользователя."""
    id: int = Field(..., description="ID транзакции")
    transaction_id: str = Field(..., description="Уникальный идентификатор транзакции в стороннем сервисе")
    amount: float = Field(..., description="Сумма транзакции")


class UsersWithAccounts(BaseModel):
    """Схема для получения пользователей с аккаунтами."""
    id: int = Field(..., description="ID пользователя")
    email: EmailStr = Field(..., description="Email пользователя")
    full_name: str = Field(..., description="ФИО пользователя")
    accounts: List[AccountSchema] = Field(..., description="Список аккаунтов пользователя")


class WebhookRequestSchema(BaseModel):
    """Схема для работы с вебхуком."""
    transaction_id: str = Field(..., min_length=36, max_length=36, description="ID транзакции")
    account_id: int = Field(..., description="ID счета пользователя")
    user_id: int = Field(..., description="ID пользователя", exclude=True)
    amount: float = Field(..., description="Сумма транзакции")
    signature: str = Field(..., description="Подпись транзакции")
