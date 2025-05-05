from pydantic import BaseModel


class CreateUser(BaseModel):
    """Схема для создания пользователя."""

    email: str
    username: str
    first_name: str
    last_name: str
    password: str


class UpdateUser(BaseModel):
    """Схема для обновления пользователя."""

    email: str
    username: str
    first_name: str
    last_name: str
    password: str
    is_active: bool
    is_admin: bool