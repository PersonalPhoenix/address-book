import logging
from typing import Optional, Any

from src.redis.redis_client import redis_client


logger = logging.getLogger(__name__)


class RedisDAO:
    """Базовый DAO для работы с Redis"""

    @staticmethod
    async def get(key: str) -> Optional[Any]:
        """Получение значения по ключу"""
        return await redis_client.get(key)

    @staticmethod
    async def set(key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Сохранение значения"""
        return await redis_client.set(key, value, ttl)

    @staticmethod
    async def exists(key: str) -> bool:
        """Проверка существования ключа"""
        return await redis_client.exists(key)

    @staticmethod
    async def delete(key: str) -> bool:
        """Удаление ключа"""
        return await redis_client.delete(key)

    @staticmethod
    async def update(key: str, update_data: dict, ttl: Optional[int] = None) -> bool:
        """Обновление словаря по ключу"""
        existing_data = await RedisDAO.get(key)

        if existing_data is None:
            return False

        if not isinstance(existing_data, dict):
            logger.warning(
                f'Key {key} contains non-dict data: {type(existing_data)}'
            )
            return False

        existing_data.update(update_data)

        return await RedisDAO.set(key, existing_data, ttl)
