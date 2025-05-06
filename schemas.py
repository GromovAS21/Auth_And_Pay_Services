from typing import List

from pydantic import BaseModel, EmailStr, Field


class CreateUser(BaseModel):
    """Схема для создания пользователя."""

    email: EmailStr = Field(..., description="Email пользователя")
    username: str = Field(..., min_length=2, max_length=50, description="Логин пользователя")
    first_name: str = Field(..., min_length=2, max_length=50, description="Имя пользователя")
    last_name: str = Field(..., min_length=2, max_length=50, description="Фамилия пользователя")
    password: str = Field(..., min_length=8, description="Пароль")


class UpdateUser(CreateUser):
    """Схема для обновления пользователя."""

    password: None = Field(None, exclude=True)
    is_active: bool = Field(default=True, description="Активный статус пользователя")
    is_admin: bool = Field(default=False, description="Админ статус пользователя")


class User(BaseModel):
    """Схема для получения пользователя."""

    id: int = Field(..., description="ID пользователя")
    email: EmailStr = Field(..., description="Email пользователя")
    full_name: str = Field(..., description="ФИО пользователя")

class Account(BaseModel):
    """Схема для получения аккаунта пользователя."""
    id: int = Field(..., description="ID аккаунта")
    total: float = Field(..., description="Баланс пользователя")


class UsersWithAccounts(BaseModel):
    """Схема для получения пользователей с аккаунтами."""
    id: int = Field(..., description="ID пользователя")
    email: EmailStr = Field(..., description="Email пользователя")
    full_name: str = Field(..., description="ФИО пользователя")
    accounts: List[Account] = Field(..., description="Список аккаунтов пользователя")
