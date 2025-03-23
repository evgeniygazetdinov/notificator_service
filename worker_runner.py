import asyncio
import logging
from lib.queue.consumer import NotificationConsumer


async def run_workers():
    """Запуск воркеров для обработки уведомлений"""
    email_consumer = NotificationConsumer()
    sms_consumer = NotificationConsumer()

    try:
        await asyncio.gather(
            email_consumer.process_notification("email"),
            sms_consumer.process_notification("sms"),
        )
    except Exception as e:
        logging.error(f"Error in workers: {str(e)}")
    finally:
        await email_consumer.close()
        await sms_consumer.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.info("Starting workers...")
    asyncio.run(run_workers())
