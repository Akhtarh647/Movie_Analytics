FROM python:3.11-slim

# Install system dependencies needed for PostgreSQL communication
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your script directly from the root of your workspace
COPY app.py .

EXPOSE 8080

# Execute uvicorn pointing to app.py
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]