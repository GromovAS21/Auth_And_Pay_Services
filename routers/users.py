from typing import Annotated

from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from database.db_depends import get_db
from models.accounts import Account
from models.transactions import Transaction
from models.users import User
from routers.auth import get_current_user, bcrypt_context

from schemas import CreateUser

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(
        db: Annotated[AsyncSession, Depends(get_db)],
        get_user: Annotated[dict, Depends(get_current_user)],
        user: CreateUser
):
    """Создание пользователя и счета для данного пользователя."""
    if not get_user["is_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission",
        )

    await db.execute(insert(User).values(
        email=user.email,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        hashed_password=bcrypt_context.hash(user.password)
    ))
    new_user = await db.scalar(select(User).where(User.email == user.email))
    await db.execute(insert(Account).values(user_id=new_user.id))
    await db.commit()
    return {"status_code": status.HTTP_201_CREATED, "transaction": "Successful"}


@router.get("/{user_id}")
async def get_user_data(
        db: Annotated[AsyncSession, Depends(get_db)],
        user_id: int,
        get_user: Annotated[dict, Depends(get_current_user)]
):
    """Получение данных о себе."""
    if not user_id == get_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You can't get someone else's data"
        )
    user = await db.scalar(select(User).where(User.id == user_id))
    return {
        "id": user.id,
        "email": user.email,
        "full_name": f"{user.first_name} {user.last_name}"
    }


@router.get("/{user_id}/accounts")
async def get_accounts_user(
        db: Annotated[AsyncSession, Depends(get_db)],
        user_id: int,
        get_user: Annotated[dict, Depends(get_current_user)]
):
    """Получение списка счетов и баланса пользователя."""
    if get_user["is_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The admin has no accounts"
        )
    if user_id != get_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You can't get someone else's accounts"
        )
    accounts = await db.scalars(select(Account).where(Account.user_id == user_id))
    return accounts.all()


@router.get("/{user_id}/transactions")
async def get_transactions_user(
        db: Annotated[AsyncSession, Depends(get_db)],
        user_id: int,
        get_user: Annotated[dict, Depends(get_current_user)]
):
    """Получение платежей пользователя"""
    if get_user["is_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The admin has no transactions"
        )
    if user_id != get_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You can't get someone else's transactions"
        )
    transactions = await db.scalars(select(Transaction).where(Transaction.user_id == user_id))
    return transactions.all()

