"""Модуль для работы с пользователями."""

from typing import Annotated, List, Sequence

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
) -> dict:
    """
    Создание пользователя и счета для данного пользователя.

    Args:
        db (AsyncSession): Объект сессии базы данных.
        get_user (dict): Текущий пользователь.
        user (CreateUserSchema): Объект данных пользователя.

    Returns:
        dict: Статус код и сообщение об успешном создании пользователя и счета.

    Raises:
        HTTPException: Если пользователь уже зарегистрирован или не имеет прав администратора.
    """
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
) -> List[dict]:
    """
    Получение списка пользователей и списка его счетов с балансами.

    Args:
        db (AsyncSession): Объект сессии базы данных.
        get_user (dict): Текущий пользователь.

    Returns:
        List[dict]: Список пользователей и их счетов с балансами.

    Raises:
        HTTPException: Если у пользователя нет прав администратора.
    """
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
) -> dict:
    """
    Обновление данных пользователя.

    Args:
        db (AsyncSession): Объект сессии базы данных.
        get_user (dict): Текущий пользователь.
        user_id (int): Идентификатор пользователя.
        update_data (UpdateUserSchema): Объект данных пользователя.

    Returns:
        dict: Статус код и сообщение об успешном обновлении данных пользователя.

    Raises:
        HTTPException: Если пользователь не найден или не имеет прав администратора.

    """
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
) -> dict:
    """
    Получение данных о пользователе.

    Args:
        db (AsyncSession): Объект сессии базы данных.
        user_id (int): Идентификатор пользователя.
        get_user (dict): Текущий пользователь.

    Returns:
        dict: Словарь с данными о пользователе.

    Raises:
        HTTPException: Если пользователь не найден или не имеет прав администратора.
    """
    if not get_user["is_admin"] and user_id != get_user["id"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You can't get someone else's data")
    user = await db.scalar(select(User).where(User.id == user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return {"id": user.id, "email": user.email, "full_name": f"{user.first_name} {user.last_name}"}


@router.delete("/{user_id}")
async def delete_user(
    db: Annotated[AsyncSession, Depends(get_db)], user_id: int, get_user: Annotated[dict, Depends(get_current_user)]
) -> dict:
    """
    Удаление пользователя. Перевод поля is_active в False.

    Args:
        db (AsyncSession): Объект сессии базы данных.
        user_id (int): Идентификатор пользователя.
        get_user (dict): Текущий пользователь.

    Returns:
        dict: Статус код и сообщение об успешном удалении пользователя.

    Raises:
        HTTPException: Если пользователь не найден или не имеет прав администратора
        или пытается удалить администратора.
    """
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
) -> Sequence[Account]:
    """
    Получение списка счетов и баланса пользователя.

    Args:
        db (AsyncSession): Объект сессии базы данных.
        user_id (int): Идентификатор пользователя.
        get_user (dict): Текущий пользователь.

    Returns:
        Sequence[Account]: Список счетов и баланса пользователя.

    Raises:
        HTTPException: Если пользователь не найден или не имеет прав администратора
        или пытается получить счета другого пользователя.
    """
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
) -> Sequence[Transaction]:
    """
    Получение платежей пользователя.

    Args:
        db (AsyncSession): Объект сессии базы данных.
        user_id (int): Идентификатор пользователя.
        get_user (dict): Текущий пользователь.

    Returns:
        Sequence[Transaction]: Список транзакций пользователя.

    Raises:
        HTTPException: Если пользователь не найден или не имеет прав администратора
        или пытается получить транзакции другого пользователя.
    """
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
