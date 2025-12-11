from fastapi import FastAPI

from src.address_book.endpoints.api_router import (
    router as api_address_book_router,
)
from src.redis.redis_client import redis_client


app = FastAPI(
    title='Address-Book',
    version='1.0.0',
    description='Сервис для хранения и управления связками "телефон-адрес"',
)


app.include_router(
    router=api_address_book_router,
)


@app.on_event("startup")
async def startup_event():
    """Инициализация при старте приложения"""
    await redis_client.connect()


@app.on_event("shutdown")
async def shutdown_event():
    """Очистка при завершении приложения"""
    if hasattr(redis_client, 'close'):
        await redis_client.close()
