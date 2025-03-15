FROM python:3.12-slim as base

WORKDIR /app

# Базовые зависимости для всех сервисов
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем общий код
COPY lib ./lib
COPY settings.py .
COPY worker_runner.py .

# Настройка окружения
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Stage для API
FROM base as api
COPY main.py .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Stage для worker
FROM base as worker
CMD ["python",  "worker_runner.py"]