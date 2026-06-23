FROM python:3.11-slim

RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

# SECURITY: Production-ready non-root user aur group
RUN groupadd -r appgroup && useradd -r -g appgroup -m -d /home/appuser appuser

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chown -R appuser:appgroup /app
USER appuser

EXPOSE 8080

# Production Flask WSGI server handler
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]