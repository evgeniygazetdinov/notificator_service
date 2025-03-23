import json
import os
from typing import Dict, Any

from sqlalchemy.orm import class_mapper
import aio_pika
import settings


class RabbitMQ:
    """
    RabbitMQ класс:
        Базовый класс для работы с очередью
        Устанавливает соединение
        Создает необходимые очереди
    NotificationProducer:
        Отправляет сообщения в очередь
        Выбирает нужную очередь на основе типа уведомления
        Сериализует данные в JSON
    NotificationConsumer:
        Получает сообщения из очереди
        Обрабатывает их через callback-функцию
        Подтверждает успешную обработку (ack)
        Возвращает в очередь при ошибке (nack)
    """

    def __init__(self):
        self.username = os.getenv("RABBITMQ_USER", "user")
        self.password = os.getenv("RABBITMQ_PASSWORD", "passwordmq")
        self.host = os.getenv("RABBITMQ_HOST", "localhost")
        self.port = int(os.getenv("RABBITMQ_PORT", 5672))
        self.connection = None
        self.channel = None

    async def connect(self):
        """Установка асинхронного соединения с RabbitMQ"""
        if not self.connection or self.connection.is_closed:
            self.connection = await aio_pika.connect_robust(
                f"amqp://{self.username}:{self.password}@{self.host}:{self.port}/"
            )
            self.channel = await self.connection.channel()

    async def close(self):
        """Закрытие соединения"""
        if self.connection and not self.connection.is_closed:
            await self.connection.close()
            self.connection = None
            self.channel = None


def serialize_sqlalchemy(obj):
    """Сериализация SQLAlchemy объекта в dict"""
    if hasattr(obj, "__dict__"):
        fields = {}
        for field in [x.key for x in class_mapper(obj.__class__).iterate_properties]:
            data = obj.__dict__.get(field)
            try:
                json.dumps(data)  # проверка что данные можно сериализовать
                fields[field] = data
            except TypeError:
                fields[field] = str(data)  # для объектов которые нельзя напрямую сериализовать
        return fields
    return str(obj)
