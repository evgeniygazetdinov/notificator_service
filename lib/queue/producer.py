import json
import logging

import pika

from lib.queue.base import RabbitMQ


class NotificationProducer(RabbitMQ):
    """ отправляем сообщения в очередь"""

    def send_notification(self, notification_type: str, notification_data: dict) -> None:
        """ уведомления в соответствующую очередь по типу"""
        queue_name = f'{notification_type}_notifications'
        try:
            self.channel.basic_publish(exchange='',
            routing_key=queue_name, body=json.dumps(notification_data),
            properties=pika.BasicProperties(
                delivery_mode=2,  # сохраним на диск локально
            )
            )
        except Exception as e:
            logging.error("Error sending notification: %s", e)
            raise   