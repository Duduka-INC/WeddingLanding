# Сборка: docker build -t wedding-landing .
# Запуск: docker run -p 8000:8000 wedding-landing
# С сохранением БД на хосте: docker run -p 8000:8000 -v путь/к/wedding.db:/app/wedding.db wedding-landing

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
