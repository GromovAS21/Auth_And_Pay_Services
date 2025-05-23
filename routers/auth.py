"""Модуль аутентификации."""

from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import APIRouter, HTTPException, status
from fastapi.params import Depends
from fastapi.security import HTTPBasic, OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import config
from database.db_depends import get_db
from models.users import User


router = APIRouter(prefix="/auth", tags=["auth"])

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBasic()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


async def authenticate_user(db: Annotated[AsyncSession, Depends(get_db)], username: str, password: str) -> User:
    """
    Аутентификация пользователя.

    Args:
        db(AsyncSession): Сессия базы данных.
        username(str): Имя пользователя.
        password(str): Пароль пользователя.

    Returns:
        User: Объект пользователя, если аутентификация успешна, иначе вызывается исключение.

    Raises:
        HTTPException: Если аутентификация не удалась.
    """
    user = await db.scalar(select(User).where(User.username == username))
    if not user or not bcrypt_context.verify(password, user.password) or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def create_access_token(
    user_id: int,
    username: str,
    is_admin: bool,
    expires_delta: timedelta,
) -> bytes:
    """
    Создание токена.

    Args:
        user_id(int): Идентификатор пользователя.
        username(str): Имя пользователя.
        is_admin(bool): Флаг администратора.
        expires_delta(timedelta): Срок действия токена.

    Returns:
        bytes: Токен.
    """
    payload = {
        "username": username,
        "id": user_id,
        "is_admin": is_admin,
        "exp": datetime.now(timezone.utc) + expires_delta,
    }
    payload["exp"] = int(payload["exp"].timestamp())
    return jwt.encode(payload, config.SECRET_KEY, algorithm=config.ALGORITHM)


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> dict:
    """
    Предоставления пользователя.

    Args:
        token(str): Токен пользователя.

    Returns:
        dict: Объект пользователя, если токен действителен, иначе вызывается исключение.

    Raises:
        HTTPException: Если токен не действителен.
    """
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        username: str | None = payload.get("username")
        user_id: int | None = payload.get("id")
        is_admin: bool | None = payload.get("is_admin")
        expire: int | None = payload.get("exp")

        if username is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate user",
            )
        if expire is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No access token supplied",
            )

        if not isinstance(expire, int):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token format")

        current_time = datetime.now(timezone.utc).timestamp()

        if expire < current_time:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired!")

        return {
            "username": username,
            "id": user_id,
            "is_admin": is_admin,
        }

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired!")
    except jwt.exceptions:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user")


@router.post("/token")
async def login(
    db: Annotated[AsyncSession, Depends(get_db)],
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> dict:
    """
    Авторизация пользователя.

    Args:
        db(AsyncSession): Сессия базы данных.
        form_data(OAuth2PasswordRequestForm): Форма авторизации пользователя.

    Returns:
        dict: Токен пользователя.
    """
    user = await authenticate_user(db, form_data.username, form_data.password)
    token = await create_access_token(
        user.id,
        user.username,
        user.is_admin,
        expires_delta=timedelta(minutes=100),
    )

    return {"access_token": token, "token_type": "bearer"}
