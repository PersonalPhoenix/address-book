from fastapi import APIRouter

from src.address_book.endpoints.api.endpoints import (
    router as address_book_router,
)


router = APIRouter(
    tags=['API V1'],
    prefix='/v1',
)

router.include_router(address_book_router)
