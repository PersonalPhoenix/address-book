from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Класс настроек приложения"""

    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int
    REDIS_TTL: int

    class Config:
        env_file = '.env'
        case_sensitive = True


settings = Settings()
