FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements-backend.txt .
RUN pip install --no-cache-dir -r requirements-backend.txt

# Copy project
COPY . .

# Create necessary directories
RUN mkdir -p logs media staticfiles

# Run migrations and collect static
RUN python manage.py collectstatic --noinput || true

EXPOSE 8000

CMD ["gunicorn", "sura_smart_backend.wsgi:application", "--bind", "0.0.0.0:8000"]
