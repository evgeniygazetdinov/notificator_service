import json
import logging
import pika
from .base import RabbitMQ, serialize_sqlalchemy

logger = logging.error


class NotificationProducer(RabbitMQ):
    """ отправляем уведомления в очередь """
    
    def send_notification(self, notification_type: str, notification_data) -> None:
        """ уведомления в соответствующую очередь по типу"""
        queue_name = f'{notification_type}_notifications'
        try:
            # Преобразуем SQLAlchemy модель в dict и затем в JSON
            message_data = serialize_sqlalchemy(notification_data)
            message_body = json.dumps(message_data)
            
            self.channel.basic_publish(
                exchange='',
                routing_key=queue_name,
                body=message_body,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # сохраним на диск локально
                )
            )
        except Exception as e:
            logger("Error sending notification: %s", e)
            raise