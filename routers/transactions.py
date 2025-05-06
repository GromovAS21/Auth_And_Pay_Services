from typing import Annotated

import sqlalchemy
from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from database.db_depends import get_db
from models.accounts import Account
from models.transactions import Transaction
from models.users import User
from routers.auth import get_current_user
from routers.services.webhook import verify_signature
from schemas import WebhookRequestSchema

router = APIRouter(prefix="/transaction", tags=["transactions"])


@router.post("/payment")
async def payment(
        db: Annotated[AsyncSession,Depends(get_db)],
        payment_data: WebhookRequestSchema,
        get_user: Annotated[dict, Depends(get_current_user)]

):
    """"Запрос на создание платежа"""
    if not await verify_signature(payment_data):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid signature"
        )
    user = await db.scalar(select(User).where(User.id == payment_data.user_id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not found"
        )
    if get_user["id"] != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="invalid user specified"
        )
    account = await db.scalar(select(Account).where(Account.id == payment_data.account_id))
    if not account:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account not found"
        )
    if account.user_id != get_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The account specified is not the current user"
        )
    account.total += payment_data.amount
    try:
        await db.execute(insert(Transaction).values(
            transaction_id=payment_data.transaction_id,
            account_id=payment_data.account_id,
            user_id=payment_data.user_id,
            amount=payment_data.amount
        ))
    except sqlalchemy.exc.IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Transaction already exists"
        )
    await db.commit()
    return {
        "status_code": status.HTTP_200_OK,
        "transaction": "payment successful"
    }

