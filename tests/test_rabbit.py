import json
import pytest
from unittest.mock import Mock, AsyncMock, patch
from lib.queue.consumer import NotificationConsumer
from lib.queue.producer import NotificationProducer
from lib.schemas import NotificationCreate
from lib.services.email import EmailService


# Фикстуры
@pytest.fixture
async def producer():
    """Фикстура для асинхронного producer"""
    producer = NotificationProducer()
    await producer.connect()
    try:
        yield producer
    finally:
        await producer.close()


@pytest.fixture
async def consumer():
    """Фикстура для асинхронного consumer"""
    consumer = NotificationConsumer()
    await consumer.connect()
    try:
        yield consumer
    finally:
        await consumer.close()


@pytest.fixture
def mock_email_service():
    """Мок для email сервиса"""
    with patch.object(EmailService, "send_email", new_callable=AsyncMock) as mock:
        yield mock


# Тесты
@pytest.mark.asyncio
async def test_producer_sends_message(producer):
    """Тест отправки сообщения в очередь"""
    notification = NotificationCreate(
        type="email",
        recipient="test@example.com",
        subject="Test Subject",
        body="Test message",
    ).model_dump()

    # Отправляем сообщение
    await producer.send_notification("email", notification)

    # Проверяем что сообщение в очереди
    queue = await producer.channel.declare_queue("email_notifications")
    message = await queue.get()
    assert message is not None

    # Проверяем содержимое сообщения
    message_data = json.loads(message.body.decode())
    assert message_data["recipient"] == "test@example.com"
    assert message_data["subject"] == "Test Subject"
    assert message_data["body"] == "Test message"
    await message.ack()


@pytest.mark.asyncio
async def test_consumer_processes_email(consumer, producer, mock_email_service):
    """Тест обработки email сообщения"""
    # Создаем тестовое сообщение
    test_message = {
        "id": "123",
        "type": "email",
        "recipient": "test@example.com",
        "subject": "Test Subject",
        "body": "Test message",
    }

    # Отправляем сообщение
    await producer.send_notification("email", test_message)

    # Запускаем обработку сообщения
    queue = await consumer.channel.declare_queue("email_notifications")
    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process():
                await consumer._send_email(json.loads(message.body.decode()))
            break

    # Проверяем что email был отправлен
    mock_email_service.assert_called_once_with(
        recipients=["test@example.com"], subject="Test Subject", body="Test message"
    )


@pytest.mark.asyncio
async def test_email_service_error_handling(consumer, producer, mock_email_service):
    """Тест обработки ошибок при отправке email"""
    # Настраиваем мок для генерации ошибки
    mock_email_service.side_effect = Exception("Email service error")

    # Создаем тестовое сообщение
    test_message = {
        "id": "124",
        "type": "email",
        "recipient": "test@example.com",
        "subject": "Test Subject",
        "body": "Test message",
    }

    # Отправляем сообщение
    await producer.send_notification("email", test_message)

    # Проверяем что ошибка обрабатывается корректно
    with pytest.raises(Exception) as exc_info:
        queue = await consumer.channel.declare_queue("email_notifications")
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    await consumer._send_email(json.loads(message.body.decode()))
                break

    assert str(exc_info.value) == "Email service error"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_full_notification_flow():
    """
    Интеграционный тест полного цикла обработки уведомления
    Требует запущенного RabbitMQ
    """
    producer = NotificationProducer()
    consumer = NotificationConsumer()

    await producer.connect()
    await consumer.connect()

    try:
        # Создаем тестовое уведомление
        notification = {
            "id": "125",
            "type": "email",
            "recipient": "test@example.com",
            "subject": "Integration Test",
            "body": "Integration test message",
        }

        # Отправляем уведомление
        await producer.send_notification("email", notification)

        # Запускаем обработку
        queue = await consumer.channel.declare_queue("email_notifications")
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    message_data = json.loads(message.body.decode())
                    assert message_data["id"] == "125"
                    assert message_data["recipient"] == "test@example.com"
                break

    finally:
        await producer.close()
        await consumer.close()
