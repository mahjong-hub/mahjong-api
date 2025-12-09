# Use official Python runtime as base image
FROM python:3.13-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY Pipfile Pipfile.lock* ./
RUN pip install pipenv && pipenv install --system --deploy

# Copy project
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput || true

# Expose port
EXPOSE 8000

# Run gunicorn
CMD ["gunicorn", "mahjong_api.wsgi:application" , \
     "--bind", "0.0.0.0:8000", \
     "--workers", "2", \
     "--log-level", "info", \
     "--timeout", "60"]
