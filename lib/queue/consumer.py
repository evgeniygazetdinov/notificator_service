import json
import logging
import time
from typing import Callable, Dict, Any, Optional

import pika

from .base import RabbitMQ
from sqlalchemy.orm import Session
from lib.crud import notification as notification_crud
from lib.db import SessionLocal

logger = logging.getLogger(__name__)

class NotificationConsumer(RabbitMQ):
    """Класс для получения и обработки уведомлений из очереди"""
    QUEUE_NAMES = {
        'email': 'email_notifications',
        'sms': 'sms_notifications'
    }

    def __init__(self, max_retries: int = 3, retry_delay: int = 5):
        super().__init__()
        self.db: Session = SessionLocal()
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    def process_notification(self, notification_type: str):
        """
        Начать обработку уведомлений определенного типа
        
        Args:
            notification_type: тип уведомлений для обработки (email/sms)
        """
        queue_name = self.QUEUE_NAMES.get(notification_type)
        if not queue_name:
            raise ValueError(f"Unsupported notification type: {notification_type}")
        
        def callback(ch, method, properties, body):
            notification_id = None
            retry_count = properties.headers.get('x-retry-count', 0) if properties.headers else 0

            try:
                notification_data = json.loads(body)
                notification_id = notification_data.get('id')
                
                if not notification_id:
                    logger.error("No notification ID in message")
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                    return

                # Проверяем существование уведомления
                notification = notification_crud.get_notification(self.db, notification_id)
                if not notification:
                    logger.error(f"Notification {notification_id} not found in database")
                    # Если превышено количество попыток, отбрасываем сообщение
                    if retry_count >= self.max_retries:
                        logger.error(f"Max retries ({self.max_retries}) reached for notification {notification_id}")
                        ch.basic_ack(delivery_tag=method.delivery_tag)
                    else:
                        # Возвращаем в очередь с увеличенным счетчиком попыток
                        time.sleep(self.retry_delay)  # Ждем перед повторной попыткой
                        ch.basic_publish(
                            exchange='',
                            routing_key=queue_name,
                            body=body,
                            properties=pika.BasicProperties(
                                headers={'x-retry-count': retry_count + 1}
                            )
                        )
                        ch.basic_ack(delivery_tag=method.delivery_tag)
                    return

                # Обновляем статус на processing
                notification_crud.update_notification(
                    self.db, 
                    notification_id,
                    {"status": "processing"}
                )
                
                # В зависимости от типа уведомления вызываем соответствующий обработчик
                if notification_type == 'email':
                    self._send_email(notification_data)
                elif notification_type == 'sms':
                    self._send_sms(notification_data)
                
                # Обновляем статус на sent
                notification_crud.update_notification(
                    self.db, 
                    notification_id,
                    {"status": "sent"}
                )
                logger.info(f"Successfully processed notification {notification_id}")
                ch.basic_ack(delivery_tag=method.delivery_tag)
                
            except Exception as e:
                logger.error(f"Error processing notification {notification_id}: {str(e)}")
                if notification_id:
                    notification_crud.update_notification(
                        self.db, 
                        notification_id,
                        {'status': "failed"}
                    )
                # Добавляем задержку перед повторной попыткой
                time.sleep(self.retry_delay)
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

        # Устанавливаем prefetch_count в 1, чтобы получать сообщения по одному
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(
            queue=queue_name,
            on_message_callback=callback
        )
        
        logger.info(f"Started consuming from {queue_name}")
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            self.channel.stop_consuming()
        finally:
            self.close()
            self.db.close()
    
    def _send_email(self, notification_data: Dict[str, Any]):
        """
        Отправка email уведомления
        В реальном приложении здесь будет интеграция с email-провайдером
        """
        print(f"Sending email to {notification_data['recipient']}")
        # TODO: Добавить реальную отправку email
    
    def _send_sms(self, notification_data: Dict[str, Any]):
        """
        Отправка SMS уведомления
        В реальном приложении здесь будет интеграция с SMS-провайдером
        """
        print(f"Sending SMS to {notification_data['recipient']}")
        # TODO: Добавить реальную отправку SMS