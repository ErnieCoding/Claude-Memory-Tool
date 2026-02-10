FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

RUN mkdir -p storage/user_files storage/responses

EXPOSE 5000

CMD ["python", "-m", "flask", "--app", "app:create_app()", "run", "--host=0.0.0.0", "--port=5000"]
