from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.address_book.endpoints.api_router import (
    router as api_address_book_router,
)
from src.redis.redis_client import redis_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    await redis_client.connect()

    yield

    if hasattr(redis_client, 'close'):
        await redis_client.close()


app = FastAPI(
    title='Address-Book',
    version='1.0.0',
    description='Сервис для хранения и управления связками "телефон-адрес"',
    lifespan=lifespan,
)


app.include_router(
    router=api_address_book_router,
)
