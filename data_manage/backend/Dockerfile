FROM python:3.11-slim

WORKDIR /app

COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

COPY data_manager /app/data_manager
COPY backend /app/backend

ENV PYTHONPATH=/app
WORKDIR /app/backend

RUN mkdir -p /app/backend/data

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
