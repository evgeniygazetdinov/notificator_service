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

    @property
    def database_url(self) -> str:
        """Динамически создаем URL базы данных из компонентов"""
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()

# Используем динамически созданный URL
SQLALCHEMY_DATABASE_URL = settings.database_url
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()