import json
from typing import Optional, Any

from src.redis.redis_client import redis_client


class RedisDAO:
    """Базовый DAO для работы с Redis"""

    @staticmethod
    async def get(key: str) -> Optional[Any]:
        """Получение значения по ключу"""
        return await redis_client.get(key)

    @staticmethod
    async def set(key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Сохранение значения"""
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value)

            if ttl:
                return await redis_client.setex(key, ttl, value)
            else:
                return await redis_client.set(key, value)
        except Exception:
            return False

    @staticmethod
    async def exists(key: str) -> bool:
        """Проверка существования ключа"""
        return await redis_client.exists(key) > 0

    @staticmethod
    async def delete(key: str) -> bool:
        """Удаление ключа"""
        return await redis_client.delete(key) > 0

    @staticmethod
    async def update(key: str, update_data: dict, ttl: Optional[int] = None) -> bool:
        """Обновление значения по ключу"""
        existing_data = await RedisDAO.get(key)

        if existing_data is None:
            return False

        if isinstance(existing_data, dict):
            existing_data.update(update_data)
            updated_data = existing_data
        else:
            updated_data = update_data

        return await RedisDAO.set(key, updated_data, ttl)
