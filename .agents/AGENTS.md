# AGENTS.md

This file provides guidance to AI Agents when working with code in this repository.

## Project Overview

Mahjong API is a Django REST Framework backend for a mahjong tile detection mobile app. Users upload photos of their mahjong hand, and the system uses computer vision (YOLO via Modal.com) to detect and identify tiles. Images are stored on Cloudflare R2 and the API is hosted on Render.com.

## Commands

```bash
# Package management uses pipenv
pipenv install --dev          # Install dependencies
pipenv shell                  # Activate virtualenv

# Development
pipenv run start              # Run dev server (python manage.py runserver)
pipenv run shell              # Django shell
pipenv run migrate            # Run migrations
pipenv run makemigrations     # Create migrations
pipenv run test               # Run tests (auto-detects test settings)
pipenv run new-app <name>     # Create new Django app

# Linting
pipenv run ruff check .       # Lint code
pipenv run ruff check . --fix # Auto-fix lint issues

# Run a single test
pipenv run python manage.py test <app>.tests.<TestClass>.<test_method>
```

## Architecture

### Django Apps
- **core**: Base models (`TimeStampedModel` with created_at/updated_at) and custom DRF exception handling
- **user**: `Client` model for anonymous app installs (identified by install_id)
- **asset**: Presigned R2 upload flow with upload sessions and polymorphic asset references (`AssetRef` uses GenericForeignKey)
- **hand**: Mahjong hand detection — dispatches to Modal.com for GPU inference, polls for results
- **rule**: Mahjong rule sets (placeholder)
- **modal_app**: Standalone Modal.com app — FastAPI server + YOLO inference on T4 GPU (deployed separately)

### Key Patterns

**Environment Configuration**: Typed, validated env vars via `EnvConfig`/`EnvVar` in `mahjong_api/env/`. App code should NOT import from env directly. Instead:
- Settings files (`development.py`, `production.py`, etc.) import from `mahjong_api.env`
- App code imports from `django.conf import settings`

```python
# CORRECT - use settings
from django.conf import settings
bucket = settings.STORAGE_BUCKET_IMAGES

# WRONG - don't import env directly in app code
from mahjong_api.env import env  # Only allowed in settings files
```

**Custom API Exceptions**: Inherit from `core.exceptions.BaseAPIException` (uses attrs). The custom exception handler in `core/exceptions.py` is registered in settings.

**Modal Integration**: Hand detection uses an async dispatch/poll pattern:
1. `POST /hand/detection/` → creates detection, calls Modal `/detect`, stores `call_id`
2. `GET /hand/detection/{id}/poll/` → polls Modal `/results/{call_id}`, processes result on success

### Service-Serializer-View Pattern

Follow the pattern established in the `hand` app:

**Services** (`<app>/services/<feature>.py`):
- Contain business logic and database operations
- Return Django model instances (not dataclasses)
- Use `TypedDict` for compound returns (e.g., model + ephemeral data like presigned URLs)
- Raise custom exceptions for validation errors

**Serializers** (`<app>/serializers/<feature>_serializer.py`):
- Use `ModelSerializer` for request/response handling
- Implement validation in `validate_<field>()` methods
- Use `write_only=True` for request-only fields, `read_only=True` for response-only fields

**Views** (`<app>/views/<feature>_view.py`):
- Use `GenericViewSet` with appropriate mixins
- Set `serializer_class` and implement `get_queryset()` for ownership filtering
- Use `get_serializer_context()` to pass request data (e.g., `install_id`)

### File Naming Conventions

```
<app>/
├── factories.py               # Factory Boy factories for tests
├── serializers/
│   ├── __init__.py
│   ├── <feature>_serializer.py
│   └── tests/
│       └── test_<feature>_serializer.py
├── services/
│   ├── __init__.py
│   ├── <feature>.py
│   └── tests/
│       └── test_<feature>.py
├── views/
│   ├── __init__.py
│   ├── <feature>_view.py
│   └── tests/
│       └── test_<feature>_view.py
└── models/
    ├── __init__.py
    └── <model>.py
```

**S3/R2 Operations**: All storage logic lives in `asset/services/s3.py`:
- `generate_presigned_put_url()` - For client uploads
- `generate_presigned_get_url()` - For secure read access (e.g., Modal inference)
- `head_object()` - Check if object exists

### Settings Structure

Settings use a modular `mahjong_api/settings/` directory:
- `base.py` - Shared configuration
- `local.py` - Local dev (DEBUG=True)
- `development.py` - Dev environment on Render
- `production.py` - Production on Render
- `test.py` - Tests with PostgreSQL via testcontainers
- `ci.py` - CI jobs (SQLite by default, real DB when `DATABASE_URL` is set)

Settings auto-detection in `__init__.py` selects the appropriate module based on `DJANGO_ENV` or test command detection.

### Database
- PostgreSQL in production/development (via `DATABASE_URL`)
- PostgreSQL via testcontainers in tests (matches production)
- SQLite in CI jobs that don't need a real database

### Testing

Tests use [testcontainers](https://testcontainers.com/) to spin up a PostgreSQL container automatically. Docker must be running.

Tests use Factory Boy for test data. Factories are in `<app>/factories.py`:
- `ClientFactory` (user app)
- `UploadSessionFactory`, `AssetFactory` (asset app)
- `HandFactory`, `HandDetectionFactory`, `DetectionTileFactory` (hand app)

Use `@override_settings` decorator to mock settings in tests.

## Code Style

Configured in `pyproject.toml` using ruff:
- Python 3.13+ target
- 79 char line length (86 before E501 triggers)
- Single quotes
- Uses pycodestyle, pyflakes, and flake8-bugbear rules

## CI/CD

GitHub Actions workflows in `.github/workflows/`:
- **ci-django.yml** — migration checks, lint (ruff), tests (on PR and push to main)
- **deploy-django-dev.yml** — after CI passes on main: migrate DB → deploy Render
- **deploy-prod.yml** — on tag push `v*`: CI → migrate DB → deploy Render + Modal
- **deploy-modal-dev.yml** — on `modal_app/**` changes to main: deploy Modal dev

## Deployment

- **Django API**: Render.com web service, configured via `render.yaml`
- **ML Inference**: Modal.com, deployed via `modal deploy -m modal_app.src.app`
- **Storage**: Cloudflare R2 (S3-compatible, zero egress costs)
- **Database**: Neon PostgreSQL
