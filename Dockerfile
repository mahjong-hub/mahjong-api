FROM python:3.13-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Build deps only (kept out of final image)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
  && rm -rf /var/lib/apt/lists/*

# Install deps from Pipfile.lock (no requirements.txt committed)
COPY Pipfile Pipfile.lock* ./
RUN pip install --no-cache-dir pipenv \
  && pipenv requirements > requirements.txt \
  && pip install --no-cache-dir -r requirements.txt --prefix=/install

# Copy project (needed for collectstatic)
COPY . .

# Build-time: generate hashed static files for WhiteNoise
# Use CI settings to avoid "required env var" crashes during build
RUN DJANGO_SETTINGS_MODULE=mahjong_api.settings.ci \
    python manage.py collectstatic --noinput


# ---------- runtime ----------
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Runtime deps only (no gcc / libpq-dev)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
  && rm -rf /var/lib/apt/lists/*

# Copy installed python packages from builder
COPY --from=builder /install /usr/local

# Copy project
COPY . .

# Copy collected static assets from builder
COPY --from=builder /app/staticfiles /app/staticfiles

EXPOSE 8000

CMD ["gunicorn", "mahjong_api.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2", "--log-level", "info", "--timeout", "60"]
