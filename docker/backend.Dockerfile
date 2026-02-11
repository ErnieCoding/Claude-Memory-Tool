FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

RUN mkdir -p storage/user_files storage/responses

# Устанавливаем PYTHONPATH для корректной работы абсолютных импортов
ENV PYTHONPATH=/app

EXPOSE 5000

# Production: используем Gunicorn с конфигурацией
CMD ["gunicorn", "--config", "gunicorn.conf.py", "app:create_app()"]
