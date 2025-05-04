from typing import Annotated

from fastapi import APIRouter, HTTPException, status
from fastapi.params import Depends
from fastapi.security import HTTPBasic, OAuth2PasswordRequestForm
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


async def authenticate_user(
    db: Annotated[AsyncSession, Depends(get_db)], form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    user = await db.scalar(select(User).where(User.username == form_data.username))
    if (
        not user
        or not bcrypt_context.verify(form_data.password, user.hashed_password)
        or user.is_active == False
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user