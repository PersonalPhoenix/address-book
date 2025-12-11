import logging
import json
from typing import Optional, Any

import redis

from src.config import settings


logger = logging.getLogger(__name__)


class RedisClient:
    """Базовый клиент для работы с Redis"""

    def __init__(self) -> None:
        self.client = None
        self.connect()

    def connect(self) -> None:
        """Установка соединения с Redis"""
        try:
            self.client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
            )
            self.client.ping()
            logger.info('Successfully connected to Redis')
        except Exception as e:
            logger.error(f'Failed to connect to Redis: {e}')
            self.client = None

    async def get(self, key: str) -> Optional[Any]:
        """Получение значения по ключу"""
        if not self.client:
            return None

        try:
            value = self.client.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            logger.error(f'Error getting key {key}: {e}')
        return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Сохранение значения с TTL"""
        if not self.client:
            return False

        try:
            if ttl is None:
                ttl = settings.REDIS_TTL

            serialized = json.dumps(value)
            self.client.setex(key, ttl, serialized)
            return True
        except Exception as e:
            logger.error(f'Error setting key {key}: {e}')
            return False

    async def delete(self, key: str) -> bool:
        """Удаление ключа"""
        if not self.client:
            return False

        try:
            self.client.delete(key)
            return True
        except Exception as e:
            logger.error(f'Error deleting key {key}: {e}')
            return False

    async def exists(self, key: str) -> bool:
        """Проверка существования ключа"""
        if not self.client:
            return False

        try:
            return bool(self.client.exists(key))
        except Exception as e:
            logger.error(f'Error checking key {key}: {e}')
            return False


redis_client = RedisClient()
