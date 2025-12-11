from fastapi import FastAPI

from src.address_book.endpoints.api_router import (
    router as api_address_book_router,
)


app = FastAPI(
    title='Address-Book',
    version='1.0.0',
    description='Сервис для хранения и управления связками "телефон-адрес"',
)

app.include_router(
    router=api_address_book_router,
)
