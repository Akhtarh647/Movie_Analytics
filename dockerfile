FROM python:3.11-slim

RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy everything including the templates folder
COPY . .

EXPOSE 8080

# Uvicorn aur asgi_app hata kar standard Gunicorn use karein
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]