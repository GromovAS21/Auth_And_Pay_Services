"""Модуль выполняет инициализацию FastAPI"""

from fastapi import FastAPI

from routers import auth, transactions, users


app = FastAPI(
    title="Auth_and_Pay_services",
    summary="Приложение для авторизации и просмотр счетов и платежей",
    version="0.0.1",
    redoc_url=None,
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(transactions.router)
