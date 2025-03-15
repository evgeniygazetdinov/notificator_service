from functools import lru_cache
import os
from pydantic_settings import BaseSettings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


class Settings(BaseSettings):
    # Основные настройки приложения
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Notification Service"
    
    # Настройки безопасности
    SECRET_KEY: str = "your-secret-key-here"
    DEBUG: bool = True
    
    # Настройки PostgreSQL
    POSTGRES_USER: str = "user"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "notification_db"
    POSTGRES_HOST: str = "0.0.0.0"
    POSTGRES_PORT: int = 5432

    # Настройки RabbitMQ
    RABBITMQ_HOST: str = "0.0.0.0"
    RABBITMQ_USER: str = "user"
    RABBITMQ_PASSWORD: str = "passwordmq"

    @property
    def database_url(self) -> str:
        """Динамически создаем URL базы данных из компонентов"""
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    class Config:
        case_sensitive = True
        env_file = ".env"
        # Это позволит экспортировать переменные в os.environ
        env_file_encoding = 'utf-8'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Экспортируем все настройки в переменные окружения
        for key, value in self.dict().items():
            if isinstance(value, (str, int, float, bool)):
                os.environ[key] = str(value)

"""
Декоратор @lru_cache() из модуля functools 
- это механизм кеширования результатов функции. 
LRU расшифровывается как "Least Recently Used"
 (Наименее недавно использованный).
"""
@lru_cache()
def get_settings() -> Settings:
    """Создает синглтон объект настроек"""
    return Settings()


settings = get_settings()
SQLALCHEMY_DATABASE_URL = settings.database_url
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()