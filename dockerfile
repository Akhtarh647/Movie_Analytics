FROM python:3.11-slim

# System dependencies install karein
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

# SECURITY: Production-ready non-root user aur group banayein
RUN groupadd -r appgroup && useradd -r -g appgroup -m -d /home/appuser appuser

# Work directory set karein
WORKDIR /app

# Dependencies copy aur install karein
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application code copy karein
COPY . .

# /app folder ki ownership naye user ko dein taaki permissions issue na ho
RUN chown -R appuser:appgroup /app

# USER SWITCH: Ab container root ke bajaye is secure user par chalega
USER appuser

EXPOSE 8080

# FastAPI ke liye standard Uvicorn ASGI server command
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]