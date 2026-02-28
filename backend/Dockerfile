FROM python:3.11-slim

WORKDIR /app

# System deps for psycopg2, Pillow, etc.
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc libgl1 libglib2.0-0 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:socket_app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
