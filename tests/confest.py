import pytest
import asyncio
from typing import Generator
import logging

# Настройка логирования для тестов
logging.basicConfig(level=logging.INFO)


# Создаем новый event loop для каждой тестовой сессии
@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Создает глобальный event loop для тестовой сессии."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# Настройка для всех тестов
@pytest.fixture(autouse=True)
async def setup_tests():
    """Выполняется перед каждым тестом."""
    # Здесь можно добавить общую логику инициализации
    yield
    # Здесь можно добавить общую логику очистки


# Маркер для пропуска тестов, требующих RabbitMQ
def pytest_configure(config):
    config.addinivalue_line(
        "markers", "integration: mark test as requiring external services"
    )
