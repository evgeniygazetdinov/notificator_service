import json
import pytest
from unittest.mock import Mock
from lib.models.notification import NotificationCreate

def test_producer_sends_message(producer, test_queue):
    """Тест отправки сообщения в очередь"""
    # Создаем тестовое уведомление
    notification = NotificationCreate(
        type='email',
        recipient='test@example.com',
        content='Test message'
    )
    
    # Отправляем сообщение
    producer.send_notification('email', notification)
    
    # Проверяем что сообщение в очереди
    method_frame, header_frame, body = producer.channel.basic_get(test_queue)
    assert method_frame is not None
    
    # Проверяем содержимое сообщения
    message = json.loads(body)
    assert message['recipient'] == 'test@example.com'
    assert message['content'] == 'Test message'

def test_consumer_processes_message(consumer, producer, test_queue):
    """Тест обработки сообщения consumer'ом"""
    # Mock для обработчика сообщений
    mock_callback = Mock()
    
    # Отправляем тестовое сообщение
    test_message = {'type': 'email', 'recipient': 'test@example.com'}
    producer.send_notification('email', test_message)
    
    # Запускаем обработку одного сообщения
    def stop_after_one_message(ch, method, properties, body):
        mock_callback(json.loads(body))
        ch.stop_consuming()
    
    consumer.channel.basic_consume(
        queue=test_queue,
        on_message_callback=stop_after_one_message
    )
    
    consumer.channel.start_consuming()
    
    # Проверяем что сообщение было обработано
    mock_callback.assert_called_once_with(test_message)

@pytest.mark.integration
def test_full_notification_flow(producer, consumer, test_queue):
    """Интеграционный тест полного цикла уведомления"""
    # Создаем тестовое уведомление
    notification = {
        'type': 'email',
        'recipient': 'test@example.com',
        'content': 'Test message'
    }
    
    # Список для хранения обработанных сообщений
    processed_messages = []
    
    def message_handler(ch, method, properties, body):
        processed_messages.append(json.loads(body))
        ch.basic_ack(delivery_tag=method.delivery_tag)
        ch.stop_consuming()
    
    # Настраиваем consumer
    consumer.channel.basic_consume(
        queue=test_queue,
        on_message_callback=message_handler
    )
    
    # Отправляем сообщение
    producer.send_notification('email', notification)
    
    # Запускаем обработку
    consumer.channel.start_consuming()
    
    # Проверяем результат
    assert len(processed_messages) == 1
    assert processed_messages[0]['recipient'] == 'test@example.com'