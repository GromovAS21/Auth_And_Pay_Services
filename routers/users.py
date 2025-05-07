from typing import Annotated, List

import sqlalchemy
from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from database.db_depends import get_db
from models.accounts import Account
from models.transactions import Transaction
from models.users import User
from routers.auth import bcrypt_context, get_current_user
from schemas import AccountSchema, CreateUserSchema, TransactionSchema, UpdateUserSchema, UsersWithAccounts


router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(
    db: Annotated[AsyncSession, Depends(get_db)],
    get_user: Annotated[dict, Depends(get_current_user)],
    user: CreateUserSchema,
):
    """Создание пользователя и счета для данного пользователя."""
    if not get_user["is_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission",
        )
    try:
        await db.execute(
            insert(User).values(
                email=user.email,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name,
                password=bcrypt_context.hash(user.password),
            )
        )
    except sqlalchemy.exc.IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already registered",
        )
    new_user = await db.scalar(select(User).where(User.email == user.email))
    await db.execute(insert(Account).values(user_id=new_user.id))
    await db.commit()
    return {"status_code": status.HTTP_201_CREATED, "transaction": "Successful"}


@router.get("/users-with-accounts", response_model=List[UsersWithAccounts])
async def get_users_with_accounts(
    db: Annotated[AsyncSession, Depends(get_db)], get_user: Annotated[dict, Depends(get_current_user)]
):
    """Получение списка пользователей и списка его счетов с балансами."""
    if not get_user["is_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission",
        )
    users = await db.scalars(select(User).where(User.is_active).order_by(User.id.desc()))
    users_list = []
    for user in users:
        accounts = await db.scalars(select(Account).where(Account.user_id == user.id))
        user_dict = {
            "id": user.id,
            "email": user.email,
            "full_name": f"{user.first_name} {user.last_name}",
            "accounts": [{"id": account.id, "total": account.total} for account in accounts],
        }
        users_list.append(user_dict)
    return users_list


@router.put("/{user_id}")
async def update_user(
    db: Annotated[AsyncSession, Depends(get_db)],
    get_user: Annotated[dict, Depends(get_current_user)],
    user_id: int,
    update_data: UpdateUserSchema,
):
    """Обновление данных пользователя."""
    if not get_user["is_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission",
        )
    user = await db.scalar(select(User).where(User.id == user_id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    try:
        await db.execute(update(User).where(User.id == user_id).values(**update_data.model_dump()))
        await db.commit()
    except sqlalchemy.exc.IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )
    return {"status_code": status.HTTP_200_OK, "transaction": "User update is successful"}


@router.get("/{user_id}")
async def retrieve_user(
    db: Annotated[AsyncSession, Depends(get_db)], user_id: int, get_user: Annotated[dict, Depends(get_current_user)]
):
    """Получение данных о пользователе."""
    if not get_user["is_admin"] and user_id != get_user["id"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You can't get someone else's data")
    user = await db.scalar(select(User).where(User.id == user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return {"id": user.id, "email": user.email, "full_name": f"{user.first_name} {user.last_name}"}


@router.delete("/{user_id}")
async def delete_user(
    db: Annotated[AsyncSession, Depends(get_db)], user_id: int, get_user: Annotated[dict, Depends(get_current_user)]
):
    """Удаление пользователя. Перевод поля is_active в False."""
    if not get_user["is_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission",
        )
    user = await db.scalar(select(User).where(User.id == user_id, User.is_active))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    if user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can't delete admin")
    user.is_active = False
    await db.commit()
    return {"status_code": status.HTTP_200_OK, "transaction": "User delete is successful"}


@router.get("/{user_id}/accounts", response_model=List[AccountSchema])
async def get_accounts_user(
    db: Annotated[AsyncSession, Depends(get_db)], user_id: int, get_user: Annotated[dict, Depends(get_current_user)]
):
    """Получение списка счетов и баланса пользователя."""
    if not get_user["is_admin"] and user_id != get_user["id"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You can't get someone else's accounts")
    user = await db.scalar(select(User).where(User.id == user_id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    accounts = await db.scalars(select(Account).where(Account.user_id == user_id))
    return accounts.all()


@router.get("/{user_id}/transactions", response_model=List[TransactionSchema])
async def get_transactions_user(
    db: Annotated[AsyncSession, Depends(get_db)], user_id: int, get_user: Annotated[dict, Depends(get_current_user)]
):
    """Получение платежей пользователя"""
    if not get_user["is_admin"] and user_id != get_user["id"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You can't get someone else's accounts")
    user = await db.scalar(select(User).where(User.id == user_id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    transactions = await db.scalars(select(Transaction).where(Transaction.user_id == user_id))
    return transactions.all()
