# Сборка: docker build -t wedding-api:1 .
# Запуск (БД сохраняется на хосте в /opt/wedding/data/wedding.db):
#   mkdir -p /opt/wedding/data
#   docker run -d --name wedding-api -p 127.0.0.1:8000:8000 -v /opt/wedding/data/wedding.db:/app/wedding.db --restart unless-stopped wedding-api:1

FROM python:3.12-slim

WORKDIR /app

# Зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Код приложения
COPY db.py main.py models.py ./
COPY static ./static/

# Порт
EXPOSE 8000

# SQLite создаётся в /app/wedding.db при первом запуске
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
