from fastapi import APIRouter

from src.address_book.endpoints.api_v1_router import (
    router as api_v1_router,
)


router = APIRouter(
    tags=['API'],
    prefix='/api',
)

router.include_router(api_v1_router)
