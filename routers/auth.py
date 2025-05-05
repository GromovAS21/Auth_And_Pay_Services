from datetime import timedelta, timezone, datetime
from typing import Annotated

import jwt

from fastapi import APIRouter, HTTPException, status
from fastapi.params import Depends
from fastapi.security import HTTPBasic, OAuth2PasswordRequestForm, OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import config
from database.db_depends import get_db
from models.users import User

router = APIRouter(prefix="/auth", tags=["auth"])

SECRET_KEY = config.SECRET_KEY
ALGORITHM = config.ALGORITHM

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBasic()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


async def authenticate_user(
        db: Annotated[AsyncSession, Depends(get_db)],
        username: str,
        password: str
):
    """Аутентификация пользователя."""
    user = await db.scalar(select(User).where(User.username == username))
    if (
            not user
            or not bcrypt_context.verify(password, user.password)
            or user.is_active == False
    ):
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
):
    """Создание токена."""
    payload = {
        "username": username,
        "id": user_id,
        "is_admin": is_admin,
        "exp": datetime.now(timezone.utc) + expires_delta,
    }
    payload["exp"] = int(payload["exp"].timestamp())
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    """Предоставления пользователя"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
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
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token format"
            )

        current_time = datetime.now(timezone.utc).timestamp()

        if expire < current_time:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired!"
            )

        return {
            "username": username,
            "id": user_id,
            "is_admin": is_admin,
        }

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired!"
        )
    except jwt.exceptions:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user"
        )


@router.post("/token")
async def login(
    db: Annotated[AsyncSession, Depends(get_db)],
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
):
    """Авторизация пользователя"""
    user = await authenticate_user(db, form_data.username, form_data.password)
    token = await create_access_token(
        user.id,
        user.username,
        user.is_admin,
        expires_delta=timedelta(minutes=100),
    )

    return {"access_token": token, "token_type": "bearer"}
