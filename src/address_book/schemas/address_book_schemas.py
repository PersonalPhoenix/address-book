from pydantic import BaseModel, Field


class CreatePhoneAddressesSchema(BaseModel):
    """Схема создания связки телефон-адрес"""

    phone: str = Field(
        ...,
        pattern=r'^(\+79\d{9}|89\d{9})$',
        min_length=11,
        max_length=12,
        description="""Номер телефона в формате:
        - +79XXXXXXXXX (12 символов: знак + и 11 цифр)
        - 89XXXXXXXXX (11 символов: 11 цифр)
        """
    )
    address: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description='Адрес, максимум 500 символов',
    )


class PhoneAddressResponse(BaseModel):
    """Схема ответа с адресом по телефону"""

    phone: str = Field(..., description='Номер телефона')
    address: str = Field(..., description='Адрес')

    class Config:
        json_schema_extra = {
            'example': {
                'phone': '+79XXXXXXXXX',
                'address': 'Москва, ул. Пушкина, д. 1',
            },
        }


class UpdatePhoneAddressSchema(BaseModel):
    """Схема для обновления адреса"""

    address: str = Field(
        ...,
        max_length=500,
        min_length=1,
        description='Новый адрес, максимум 500 символов',
    )


class ErrorResponse(BaseModel):
    """Схема ответа с ошибкой"""

    error: str = Field(..., description='Тип ошибки')
    detail: str = Field(..., description='Детальное описание')

    class Config:
        json_schema_extra = {
            'example': {
                'error': 'Not Found',
                'detail': 'Phone +79XXXXXXXXX not found',
            },
        }
