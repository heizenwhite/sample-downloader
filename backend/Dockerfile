FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update \
 && apt-get install -y --no-install-recommends gcc libffi-dev \
 && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# Copy app and Firebase service account
COPY app ./app
COPY serviceAccountKey.json ./serviceAccountKey.json

# Set Firebase env var
ENV FIREBASE_SERVICE_ACCOUNT=/app/serviceAccountKey.json

# Expose and run
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
