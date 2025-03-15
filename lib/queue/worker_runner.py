import logging

from lib.queue.consumer import NotificationConsumer

logger = logging.getLogger(__name__)
from multiprocessing import Process



def process_email(notification_data):
    recipient = notification_data['recipient']
    subject = notification_data['subject']
    body = notification_data['body']

    logger.info("send notification to {} with subject {}".format(recipient, subject))
    # send email here


def process_sms(notification_data):
    recipient = notification_data['recipient']
    body = notification_data['body']

    logger.info("send notification to {} with body {}".format(recipient, body))
    # send sms here



def run_worker(notification_type):
    """ роутер на смс или почту"""
    consumer = NotificationConsumer()
    consumer.process_notification(notification_type) # process_email if notification_type == 'email' else process_sms)


def run_workers():
    """ запуск процессов """
    process_list = []

    for notification_type in ['email', 'sms']:
        process = Process(
            target=run_worker, args=(notification_type,)
        )
        process.start()
        process_list.append(process)

    for process in process_list:
        process.join()