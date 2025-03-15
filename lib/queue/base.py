import json

import pika
import os

from sqlalchemy.orm import class_mapper

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
    Преимущества такого подхода:
        Надежность:
            Сообщения сохраняются на диск (delivery_mode=2)
            При ошибке возвращаются в очередь
            Не теряются при перезапуске сервиса
        Масштабируемость:
            Можно запустить несколько воркеров
            Балансировка нагрузки (prefetch_count=1)
            Разные очереди для разных типов уведомлений
        Отказоустойчивость:
            Асинхронная обработка
            Независимость от основного приложения
            Автоматические повторные попытки
    """
    def __init__(self):
        self.user = os.getenv('RABBITMQ_USER', 'user')
        self.password = os.getenv('RABBITMQ_PASSWORD', 'passwordmq')
        self.host = os.getenv('RABBITMQ_HOST', 'localhost')
        self.port = int(os.getenv('RABBITMQ_PORT', 5672))
        self.credentials = pika.PlainCredentials(self.user, self.password)
        self.parameters = pika.ConnectionParameters(host=self.host, port=self.port, credentials=self.credentials)
        self.connection = pika.BlockingConnection(self.parameters)
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='email_notifications')
        self.channel.queue_declare(queue='sms_notifications')

    def close(self):
        if self.connection and not self.connection.is_closed:
            self.connection.close()

def serialize_sqlalchemy(obj):
    """Сериализация SQLAlchemy объекта в dict"""
    if hasattr(obj, '__dict__'):
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