FROM python:3.11-slim

RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

EXPOSE 8080

# Uvicorn looks inside app.py for the asgi_app object wrapper
CMD ["uvicorn", "app:asgi_app", "--host", "0.0.0.0", "--port", "8080"]