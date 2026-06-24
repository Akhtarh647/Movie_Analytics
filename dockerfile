FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN groupadd -r appgroup && useradd -r -g appgroup -m -d /home/appuser appuser \
    && chown -R appuser:appgroup /app

COPY --chown=appuser:appgroup . .

USER appuser
EXPOSE 8080

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]