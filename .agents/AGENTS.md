# AGENTS.md

This file provides guidance to AI Agents when working with code in this repository.

## Project Overview

Mahjong API is a Django REST Framework backend for a mahjong tile detection mobile app. Users upload photos of their mahjong hand, and the system uses YOLO (via ultralytics) for ML inference to detect and identify the tiles. The API uses Celery for async task processing backed by AWS SQS.

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
- **asset**: Presigned S3 upload flow with upload sessions and polymorphic asset references (`AssetRef` uses GenericForeignKey)
- **hand**: Mahjong hand detection - Celery tasks for running ML inference
- **rule**: Mahjong rule sets (placeholder)
- **ml**: Machine learning inference, model loading, and S3 model download

### Key Patterns

**Environment Configuration**: Environment variables are loaded in `mahjong_api/env.py` using `get_required_env()` and `get_optional_env()` helpers. However, **app code should NOT import from env.py directly**. Instead:
- Settings files (`development.py`, `production.py`) import from `env.py`
- App code imports from `django.conf import settings`

Example:
```python
# CORRECT - use settings
from django.conf import settings
bucket = settings.AWS_STORAGE_BUCKET_NAME

# WRONG - don't import env directly in app code
from mahjong_api import env  # Only allowed in settings files
```

**Custom API Exceptions**: Inherit from `core.exceptions.BaseAPIException` (uses attrs). The custom exception handler in `core/exceptions.py` is registered in settings.

**Celery Tasks**: Defined in `<app>/tasks.py`. Uses SQS as broker in production, memory broker in tests. Tasks run with `CELERY_TASK_ALWAYS_EAGER=True` during tests.

### Service-Serializer-View Pattern

Follow the pattern established in the `hand` app:

**Services** (`<app>/services/<feature>.py`):
- Contain business logic and database operations
- Return Django model instances (not dataclasses)
- Use `TypedDict` for compound returns (e.g., model + ephemeral data like presigned URLs)
- Raise custom exceptions for validation errors

```python
# CORRECT - return model or TypedDict with model
class PresignResult(TypedDict):
    asset: Asset
    presigned_url: str

def create_presigned_upload(...) -> PresignResult:
    ...
    return {'asset': asset, 'presigned_url': presigned_url}

# AVOID - returning dataclasses for API responses
```

**Serializers** (`<app>/serializers/<feature>_serializer.py`):
- Use `ModelSerializer` for request/response handling
- Implement validation in `validate_<field>()` methods
- `create()` method calls service and returns model instance
- Use `write_only=True` for request-only fields, `read_only=True` for response-only fields

```python
class HandDetectionSerializer(serializers.ModelSerializer):
    asset_id = serializers.UUIDField(write_only=True)
    tiles = DetectionTileSerializer(many=True, read_only=True)

    class Meta:
        model = HandDetection
        fields = [...]
        read_only_fields = [...]

    def validate_asset_id(self, value):
        # Validation logic here
        return value

    def create(self, validated_data) -> HandDetection:
        result = trigger_hand_detection(...)
        return HandDetection.objects.get(id=result.hand_detection_id)
```

**Views** (`<app>/views/<feature>_view.py`):
- Use `GenericViewSet` with appropriate mixins (`CreateModelMixin`, `RetrieveModelMixin`, etc.)
- Set `serializer_class` and implement `get_queryset()` for ownership filtering
- Use `get_serializer_context()` to pass request data (e.g., `install_id`)
- Use `self.get_serializer()` instead of instantiating serializers directly

```python
class HandDetectionViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = HandDetectionSerializer

    def get_queryset(self):
        install_id = get_install_id(self.request)
        return HandDetection.objects.filter(hand__client__install_id=install_id)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['install_id'] = get_install_id(self.request)
        return context

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        response_serializer = self.get_serializer(instance)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
```

### File Naming Conventions

```
<app>/
├── serializers/
│   ├── __init__.py
│   ├── <feature>_serializer.py      # e.g., hand_detection_serializer.py
│   └── tests/
│       └── test_<feature>_serializer.py
├── services/
│   ├── __init__.py
│   ├── <feature>.py                 # e.g., hand_detection.py
│   └── tests/
│       └── test_<feature>.py
├── views/
│   ├── __init__.py
│   ├── <feature>_view.py            # e.g., hand_detection_view.py
│   └── tests/
│       └── test_<feature>_view.py
└── models/
    ├── __init__.py
    └── <model>.py                   # e.g., hand.py, hand_tile.py
```

**ML Model Loading**:
- `ml/inference/model.py` - Singleton pattern for YOLO model, loaded once per process via `get_model()`
- `ml/inference/model_loader.py` - Downloads model weights from S3 at Celery worker startup
- Model download is triggered by `worker_init` signal in `celery.py`
- If download fails, worker exits with code 1 so ECS can restart

**S3 Operations**: All S3 logic lives in `asset/services/s3.py`:
- `generate_presigned_put_url()` - For client uploads
- `head_object()` - Check if object exists
- `download_file()` - Download files (used for model loading)

### Settings Structure

Settings use a modular `mahjong_api/settings/` directory:
- `base.py` - Shared configuration (no env.py import)
- `development.py` - Local dev (DEBUG=True), imports env.py
- `production.py` - Production (DJANGO_ENV=production), imports env.py
- `test.py` - Tests with PostgreSQL via testcontainers, hardcoded test values
- `ci.py` - CI jobs without Docker (SQLite), hardcoded CI values

Settings auto-detection in `__init__.py` selects the appropriate module based on `DJANGO_ENV` or test command detection.

### Database
- PostgreSQL in production and local development (via DATABASE_URL)
- PostgreSQL via testcontainers in tests (matches production environment)
- SQLite in CI jobs that don't need Docker (linting, migration checks)

### Testing

Test settings (`mahjong_api/settings/test.py`) are auto-detected and configure:
- PostgreSQL via testcontainers (spins up container automatically)
- Eager Celery execution (`CELERY_TASK_ALWAYS_EAGER=True`)
- Memory-based Celery broker
- Hardcoded settings values (no env.py loading)

Use `@override_settings` decorator to mock settings in tests:
```python
from django.test import TestCase, override_settings

class MyTest(TestCase):
    @override_settings(MODEL_S3_URI='s3://bucket/key')
    def test_something(self):
        ...
```

## Code Style

Configured in `pyproject.toml` using ruff:
- Python 3.13+ target
- 79 char line length (86 before E501 triggers)
- Single quotes
- Uses pycodestyle, pyflakes, and flake8-bugbear rules

## CI/CD

CircleCI configuration in `.circleci/config.yml`:
- **check_migrations**: Uses `DJANGO_ENV=ci` (SQLite, no Docker needed)
- **lint**: Uses `DJANGO_ENV=ci` (SQLite, no Docker needed)
- **test**: Uses `DJANGO_ENV=test` with machine executor (Docker available for testcontainers)

## Deployment

ECS task definitions in `.aws/`:
- `ecs-task-def.json` - API server (Gunicorn)
- `ecs-worker-task-def.json` - Celery worker with model download

The worker downloads ML model weights from S3 on startup. Required:
- `MODEL_S3_URI` env var pointing to S3 model location
- IAM policy allowing `s3:GetObject` on the model path
