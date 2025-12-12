from typing import Annotated

from fastapi import (
    APIRouter,
    status,
    Response,
    HTTPException,
    Depends,
)
from fastapi.responses import JSONResponse

from src.address_book.dao.redis_dao import RedisDAO
from src.address_book.dependencies import get_existing_phone
from src.address_book.schemas.address_book_schemas import (
    PhoneAddressResponse,
    CreatePhoneAddressesSchema,
    UpdatePhoneAddressSchema,
    ErrorResponse,
)
from src.config import settings


router = APIRouter(
    tags=['Связки телефон-адрес'],
    prefix='/address-book',
)


@router.get(
    path='/health',
    responses={
        200: {'description': 'Сервис доступен'},
        500: {'description': 'Сервис недоступен'},
    },
    summary='Проверка доступности сервиса',
)
def check_health():
    """Проверяем доступность сервиса"""
    return Response(content='Okay', status_code=200)


@router.get(
    path='/get-address/{phone}',
    responses={
        200: {'model': PhoneAddressResponse, 'description': 'Успешный ответ'},
        404: {'model': ErrorResponse, 'description': 'Телефон не найден'},
        422: {'model': ErrorResponse, 'description': 'Передан не корректный формат номера'},
        500: {'model': ErrorResponse, 'description': 'Сервер не доступен'},
    },
    summary='Получить адрес по телефону',
)
async def get_address(
    phone: Annotated[str, Depends(get_existing_phone)],
):
    """Получаем адрес по номеру телефона"""
    return await RedisDAO.get(key=phone)


@router.post(
    path='/create-address',
    responses={
        201: {'description': 'Запись успешно создана'},
        409: {'model': ErrorResponse, 'description': 'Телефон уже существует'},
        422: {'model': ErrorResponse, 'description': 'Передан не корректный формат номера'},
        500: {'model': ErrorResponse, 'description': 'Сервер не доступен'},
    },
    summary='Создать связку телефон-адрес',
)
async def create_address(data: CreatePhoneAddressesSchema):
    """Создаем связку телефон-адрес в системе"""
    exists = await RedisDAO.exists(key=data.phone)

    if exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Телефон уже существует',
        )

    await RedisDAO.set(
        key=data.phone, 
        value=data.model_dump(),
        ttl=settings.REDIS_TTL,
    )

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            'message': 'Created', 
        },
    )


@router.patch(
    path='/update-address/{phone}',
    responses={
        200: {'description': 'Адрес успешно обновлен'},
        400: {'model': ErrorResponse, 'description': 'Переданные не корректные данные'},
        404: {'model': ErrorResponse, 'description': 'Телефон не найден'},
        422: {'model': ErrorResponse, 'description': 'Передан не корректный формат номера'},
        500: {'model': ErrorResponse, 'description': 'Сервер не доступен'},
    },
    summary='Обновить адрес по телефону в связке телефон-адрес',
)
async def update_address(
    phone: Annotated[str, Depends(get_existing_phone)],
    data: UpdatePhoneAddressSchema,
):
    """Обновляем запись о клиенте"""
    update_dict = data.model_dump(exclude_unset=True)

    if not update_dict:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Не переданы данные для обновления',
        )

    success = await RedisDAO.update(key=phone, update_data=update_dict)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Не удалось обновить запись',
        )

    updated_data = await RedisDAO.get(key=phone)

    return updated_data


@router.delete(
    path='/delete-adderess/{phone}',
    responses={
        204: {'description': 'Запись успешно удалена'},
        404: {'model': ErrorResponse, 'description': 'Телефон не найден'},
        422: {'model': ErrorResponse, 'description': 'Передан не корректный формат номера'},
        500: {'model': ErrorResponse, 'description': 'Внутренняя ошибка сервера'},
    },
    summary='Удалить связку телефон-адрес',
    description='Удаляет информацию о связи телефона и адреса из системы',
)
async def delete_address(phone: Annotated[str, Depends(get_existing_phone)]):
    """Удаляет запись из Redis"""
    deleted = await RedisDAO.delete(key=phone)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Не удалось удалить запись',
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
