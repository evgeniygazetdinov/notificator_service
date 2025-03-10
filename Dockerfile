FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ARG RUN_MODE=api
ENV RUN_MODE=$RUN_MODE
COPY entrypoint.sh .
# Скрипт запуска, который будет выбирать что запускать
RUN chmod +x entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]