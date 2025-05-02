# 1) Build stage (install deps)
FROM python:3.11-slim AS builder

WORKDIR /app

# install python deps
COPY backend/requirements.txt .
RUN pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# 2) Production image
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app

# copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# copy your backend code
COPY backend/app ./app
COPY backend/app/main.py ./main.py
COPY backend/serviceAccountKey.json ./serviceAccountKey.json

ENV FIREBASE_SERVICE_ACCOUNT=/app/serviceAccountKey.json

# expose the port the app runs on
EXPOSE 8000

# uvicorn command
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]