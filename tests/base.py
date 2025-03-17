import pytest
import pika
from lib.queue.base import RabbitMQ
from lib.queue.producer import NotificationProducer
from lib.queue.consumer import NotificationConsumer

@pytest.fixture
def rabbitmq_connection():
    """Фикстура для подключения к тестовому RabbitMQ"""
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host='localhost',
            port=35672,
            credentials=pika.PlainCredentials('user', 'passwordmq')
        )
    )
    yield connection
    connection.close()

@pytest.fixture
def test_queue(rabbitmq_connection):
    """Фикстура для создания тестовой очереди"""
    channel = rabbitmq_connection.channel()
    queue_name = 'test_notifications'
    channel.queue_declare(queue=queue_name, durable=True)
    yield queue_name
    # Очищаем очередь после теста
    channel.queue_purge(queue_name)
    channel.queue_delete(queue_name)

@pytest.fixture
def producer():
    """Фикстура для producer"""
    producer = NotificationProducer()
    yield producer
    producer.close()

@pytest.fixture
def consumer():
    """Фикстура для consumer"""
    consumer = NotificationConsumer()
    yield consumer
    consumer.close()