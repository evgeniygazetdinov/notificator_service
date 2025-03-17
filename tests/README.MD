# Запуск всех тестов
```docker-compose -f docker-compose.test.yml up --build tests```

# Запуск конкретного теста
```docker-compose -f docker-compose.test.yml run tests pytest -v tests/test_rabbitmq.py -k test_producer_sends_message```