from typing import AsyncGenerator

from database.db import Session


async def get_db() -> AsyncGenerator[AsyncGenerator, None]:
    """Создает асинхронную сессию для работы с БД."""
    async with Session() as session:
        yield session
