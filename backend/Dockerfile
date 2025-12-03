FROM python:3.13-slim

WORKDIR /app

# Install system dependencies if needed (e.g. for psycopg2, Pillow)
# libpq-dev is often needed for postgres, gcc for building some python packages
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Use standard port 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
