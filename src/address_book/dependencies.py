from typing import Annotated

from fastapi import HTTPException, status, Path, Depends

from src.address_book.dao.redis_dao import RedisDAO


async def validate_phone_format(
    phone: Annotated[
        str,
        Path(
            ...,
            regex=r'^(\+79\d{9}|89\d{9})$',
            min_length=11,
            max_length=12,
            description="""Номер телефона в формате:
            - +79XXXXXXXXX (12 символов: знак + и 11 цифр)
            - 89XXXXXXXXX (11 символов: 11 цифр)
            """
        ),
    ],
) -> str:
    """Валидирует формат телефона"""
    return phone


async def get_existing_phone(
    phone: Annotated[str, Depends(validate_phone_format)]
) -> str:
    """Зависимость для проверки существования телефона"""
    exists = await RedisDAO.exists(key=phone)
    if not exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Телефон не найден',
        )
    return phone
