import json
from typing import Callable, Dict, Any
from .base import RabbitMQ
from sqlalchemy.orm import Session
from lib.crud import notification as notification_crud
from lib.db import SessionLocal

class NotificationConsumer(RabbitMQ):
    """Класс для получения и обработки уведомлений из очереди"""
    QUEUE_NAMES = {
        'email': 'email_notifications',
        'sms': 'sms_notifications'
    }

    def __init__(self):
        super().__init__()
        self.db: Session = SessionLocal()

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
            try:
                notification_data = json.loads(body)
                
                # Обновляем статус в БД на "processing"
                notification_id = notification_data.get('id')
                if notification_id:
                    notification_crud.update_notification_status(
                        self.db, 
                        notification_id, 
                        "processing"
                    )
                
                # В зависимости от типа уведомления вызываем соответствующий обработчик
                if notification_type == 'email':
                    self._send_email(notification_data)
                elif notification_type == 'sms':
                    self._send_sms(notification_data)
                
                # Обновляем статус на "sent"
                if notification_id:
                    notification_crud.update_notification_status(
                        self.db, 
                        notification_id, 
                        "sent"
                    )
                
                # Подтверждаем обработку сообщения
                ch.basic_ack(delivery_tag=method.delivery_tag)
                
            except Exception as e:
                # При ошибке обновляем статус и возвращаем сообщение в очередь
                if notification_id:
                    notification_crud.update_notification_status(
                        self.db, 
                        notification_id, 
                        "failed",
                        error=str(e)
                    )
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
                print(f"Error processing message: {e}")
        
        # Устанавливаем prefetch_count=1, чтобы распределять нагрузку между воркерами
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(
            queue=queue_name,
            on_message_callback=callback
        )
        
        print(f"Started consuming {notification_type} notifications...")
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