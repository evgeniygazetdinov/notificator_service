import json
import logging
import aio_pika
from typing import Any, Dict, Union

from .base import RabbitMQ, serialize_sqlalchemy

logger = logging.getLogger(__name__)


class NotificationProducer(RabbitMQ):
    """Отправляем уведомления в очередь"""

    async def connect(self):
        """Установка асинхронного соединения с RabbitMQ"""
        await super().connect()
        # Создаем очереди, если они не существуют
        await self.channel.declare_queue("email_notifications")
        await self.channel.declare_queue("sms_notifications")

    async def send_notification(
        self, notification_type: str, notification_data: Union[Dict[str, Any], Any]
    ) -> None:
        """Уведомления в соответствующую очередь по типу

        Args:
            notification_type: тип уведомления (email/sms)
            notification_data: данные уведомления (словарь или SQLAlchemy модель)
        """
        if not self.channel:
            await self.connect()

        queue_name = f"{notification_type}_notifications"
        try:
            # Преобразуем данные в JSON
            message_data = serialize_sqlalchemy(notification_data)
            message_body = json.dumps(message_data).encode()

            # Создаем сообщение с persistent delivery mode
            message = aio_pika.Message(
                body=message_body, delivery_mode=aio_pika.DeliveryMode.PERSISTENT
            )

            # Публикуем сообщение в очередь
            await self.channel.default_exchange.publish(message, routing_key=queue_name)

            logger.info(f"Notification sent to queue {queue_name}")

        except Exception as e:
            logger.error(f"Error sending notification: {str(e)}")
            raise

    async def close(self):
        """Закрытие соединения"""
        if self.channel:
            await self.channel.close()
        if self.connection:
            await self.connection.close()
