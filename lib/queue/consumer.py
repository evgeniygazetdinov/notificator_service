import json
import logging
import asyncio
from typing import Dict, Any

import aio_pika

from .base import RabbitMQ
from sqlalchemy.orm import Session
from lib.crud import notification as notification_crud
from lib.db import SessionLocal
from lib.services.email import EmailService

logger = logging.getLogger(__name__)


class NotificationConsumer(RabbitMQ):
    """Класс для получения и обработки уведомлений из очереди"""

    QUEUE_NAMES = {"email": "email_notifications", "sms": "sms_notifications"}

    def __init__(self, max_retries: int = 3, retry_delay: int = 5):
        super().__init__()
        self.db: Session = SessionLocal()
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.connection = None
        self.channel = None

    async def connect(self):
        """Установка асинхронного соединения с RabbitMQ"""
        self.connection = await aio_pika.connect_robust(
            f"amqp://{self.username}:{self.password}@{self.host}:{self.port}/"
        )
        self.channel = await self.connection.channel()

    async def process_notification(self, notification_type: str):
        """
        Начать обработку уведомлений определенного типа

        Args:
            notification_type: тип уведомлений для обработки (email/sms)
        """
        queue_name = self.QUEUE_NAMES.get(notification_type)
        if not queue_name:
            raise ValueError(f"Unsupported notification type: {notification_type}")

        await self.connect()
        queue = await self.channel.declare_queue(queue_name)

        async def process_message(message: aio_pika.IncomingMessage):
            async with message.process():
                notification_id = None
                retry_count = (
                    message.headers.get("x-retry-count", 0) if message.headers else 0
                )

                try:
                    notification_data = json.loads(message.body.decode())
                    notification_id = notification_data.get("id")

                    if not notification_id:
                        logger.error("No notification ID in message")
                        return

                    # Проверяем существование уведомления
                    notification = notification_crud.get_notification(
                        self.db, notification_id
                    )
                    if not notification:
                        logger.error(
                            f"Notification {notification_id} not found in database"
                        )
                        if retry_count >= self.max_retries:
                            logger.error(
                                f"Max retries ({self.max_retries}) reached for notification {notification_id}"
                            )
                            return

                        # Возвращаем в очередь с увеличенным счетчиком попыток
                        await asyncio.sleep(self.retry_delay)
                        await self.channel.default_exchange.publish(
                            aio_pika.Message(
                                body=message.body,
                                headers={"x-retry-count": retry_count + 1},
                            ),
                            routing_key=queue_name,
                        )
                        return

                    # Обновляем статус и счетчик попыток
                    notification_crud.update_notification(
                        self.db,
                        notification_id,
                        {
                            "status": "processing",
                            "retry_count": retry_count,
                            "last_error": None,  # Очищаем ошибку при начале обработки
                        }
                    )

                    # В зависимости от типа уведомления вызываем соответствующий обработчик
                    if notification_type == "email":
                        await self._send_email(notification_data)
                    elif notification_type == "sms":
                        await self._send_sms(notification_data)

                    # Обновляем статус на sent при успешной отправке
                    notification_crud.update_notification(
                        self.db,
                        notification_id,
                        {
                            "status": "sent",
                            "retry_count": retry_count,
                            "last_error": None,
                        }
                    )
                    logger.info(
                        f"Successfully processed notification {notification_id} after {retry_count} retries"
                    )

                except Exception as e:
                    error_msg = str(e)
                    logger.error(
                        f"Error processing notification {notification_id} (attempt {retry_count + 1}): {error_msg}"
                    )
                    if notification_id:
                        notification_crud.update_notification(
                            self.db,
                            notification_id,
                            {
                                "status": "failed" if retry_count >= self.max_retries else "retry",
                                "retry_count": retry_count + 1,
                                "last_error": error_msg,
                            },
                        )
                    raise

        try:
            async with queue.iterator() as queue_iter:
                async for message in queue_iter:
                    await process_message(message)
        finally:
            await self.close()
            self.db.close()

    async def close(self):
        """Закрытие соединения"""
        if self.channel:
            await self.channel.close()
        if self.connection:
            await self.connection.close()

    async def _send_email(self, notification_data: Dict[str, Any]) -> None:
        """
        Отправка email уведомления
        """
        email_service = EmailService()
        try:
            await email_service.send_email(
                recipients=[notification_data["recipient"]],
                subject=notification_data["subject"],
                body=notification_data["body"],
            )
            logger.info(f"Email sent successfully to {notification_data['recipient']}")
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            raise

    async def _send_sms(self, notification_data: Dict[str, Any]) -> None:
        """
        Отправка SMS уведомления.
        В реальном приложении здесь будет интеграция с SMS-провайдером
        """
        print(f"Sending SMS to {notification_data['recipient']}")
        # TODO: Добавить реальную отправку SMS
