# Mahjong API

A Django REST Framework backend for mahjong tile detection. Upload images of mahjong hands and get back detected tiles using YOLO-based computer vision.

## What is Mahjong?

Mahjong is a tile-based game that originated in China. Players draw and discard tiles to form winning combinations. This API helps players by automatically detecting tiles from photos of their hand, enabling features like:

- **Hand analysis**: Identify all tiles in a player's hand
- **Scoring assistance**: Calculate potential winning hands and points
- **Learning aid**: Help new players understand tile recognition

## Features

- **Presigned R2 Uploads**: Secure, direct-to-R2 file uploads via presigned URLs
- **ML Tile Detection**: YOLO-based object detection via Modal.com (T4 GPU, pay-per-use)
- **Async Detection**: Dispatch to Modal → poll for results pattern (no background workers needed)
- **Anonymous Clients**: Track app installations without requiring user accounts

## Architecture

```mermaid
flowchart TB
    subgraph Client
        Mobile[Mobile Client]
    end

    subgraph Services
        API[Django API<br/>Render.com]
        Modal[Modal.com<br/>T4 GPU]
    end

    subgraph Storage
        R2[(Cloudflare R2)]
        DB[(Neon PostgreSQL)]
    end

    Mobile -->|1. Request presigned URL| API
    API -->|2. Return presigned URL| Mobile
    Mobile -->|3. Upload image| R2
    Mobile -->|4. POST /hand/detection/| API
    API -->|5. Submit detection| Modal
    Modal -->|6. Read image| R2
    Mobile -->|7. GET /hand/detection/:id/poll/| API
    API -->|8. Poll results| Modal
    API <--> DB
```

### Django Apps

| App         | Description                                              |
|-------------|----------------------------------------------------------|
| `core`      | Base models, custom DRF exception handling               |
| `user`      | Anonymous client tracking via `install_id`               |
| `asset`     | R2 upload sessions, asset storage, polymorphic references|
| `hand`      | Hand detection — Modal dispatch and result processing    |
| `rule`      | Mahjong rule sets (placeholder)                          |
| `modal_app` | Standalone Modal.com app — FastAPI + YOLO inference      |

## Requirements

- Python 3.13+
- PostgreSQL 16+
- Docker (for running tests)

## Quick Start

### 1. Clone and Install Dependencies

```bash
git clone <repository-url>
cd mahjong-api

pip install pipenv
pipenv install --dev
```

### 2. Set Up PostgreSQL

```bash
docker run -d \
  --name mahjong-postgres \
  -e POSTGRES_USER=mahjong \
  -e POSTGRES_PASSWORD=mahjong \
  -e POSTGRES_DB=mahjong \
  -p 5432:5432 \
  postgres:16-alpine
```

### 3. Configure Environment

Create a `.env` file in the project root:

```bash
DATABASE_URL=postgresql://mahjong:mahjong@localhost:5432/mahjong
DJANGO_SECRET_KEY=your-secret-key-here

# Cloudflare R2
AWS_ACCESS_KEY_ID=your-r2-access-key
AWS_SECRET_ACCESS_KEY=your-r2-secret-key
R2_ACCOUNT_ID=your-account-id
R2_BUCKET_IMAGES=mahjong-images-dev

# Modal (optional for local dev)
MODAL_CV_ENDPOINT=https://your-modal-endpoint
MODAL_AUTH_TOKEN=your-modal-token
```

### 4. Run Migrations and Start

```bash
pipenv run migrate
pipenv run start
```

The API will be available at `http://localhost:8000`.

## Development Commands

```bash
pipenv install --dev          # Install all dependencies
pipenv run start              # Run dev server
pipenv run migrate            # Run migrations
pipenv run makemigrations     # Create migrations
pipenv run test               # Run all tests
pipenv run ruff check .       # Lint
pipenv run ruff check . --fix # Auto-fix lint issues
```

## Testing

Tests use [testcontainers](https://testcontainers.com/) to spin up a PostgreSQL container automatically. Docker must be running.

```bash
pipenv run test                          # Run all tests
pipenv run python manage.py test hand    # Run specific app
```

Test settings are auto-detected when running `manage.py test` — no environment variables needed.

## Project Structure

```
mahjong-api/
├── asset/                 # Upload & asset management
│   ├── models/            # Asset, UploadSession, AssetRef
│   ├── services/
│   │   ├── s3.py          # R2 operations (presigned URLs)
│   │   └── uploads.py     # Upload flow
│   ├── views/
│   ├── serializers/
│   └── factories.py       # Test factories
├── core/                  # Shared utilities
│   ├── models.py          # TimeStampedModel base
│   └── exceptions.py      # Custom API exceptions
├── hand/                  # Hand detection
│   ├── models/            # Hand, HandDetection, DetectionTile
│   ├── services/
│   │   ├── hand_detection.py  # Create/find detections
│   │   ├── hand_inference.py  # Dispatch to Modal, process results
│   │   └── modal_client.py    # Modal HTTP client
│   ├── views/
│   ├── serializers/
│   └── factories.py
├── user/                  # Client tracking
│   └── factories.py
├── rule/                  # Mahjong rule sets
├── modal_app/             # Modal.com CV inference (deployed separately)
│   └── src/
│       ├── app.py         # Modal app definition
│       ├── server.py      # FastAPI endpoints
│       └── detect.py      # YOLO inference
├── mahjong_api/
│   ├── settings/          # Django settings (base, local, dev, prod, test, ci)
│   ├── env/               # EnvConfig / EnvVar system
│   └── urls.py
├── .github/workflows/     # CI/CD (GitHub Actions)
├── render.yaml            # Render.com service config
├── Pipfile
└── Pipfile.lock
```

## Deployment

| Component | Platform | Trigger |
|-----------|----------|---------|
| Django API | Render.com | Push to main (dev), tag push (prod) |
| ML Inference | Modal.com | `modal_app/**` changes (dev), tag push (prod) |
| Storage | Cloudflare R2 | — |
| Database | Neon PostgreSQL | — |

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | PostgreSQL connection string |
| `DJANGO_SECRET_KEY` | Yes | Django secret key |
| `AWS_ACCESS_KEY_ID` | Yes | R2 access key |
| `AWS_SECRET_ACCESS_KEY` | Yes | R2 secret key |
| `R2_ACCOUNT_ID` | Yes | Cloudflare R2 account ID |
| `R2_BUCKET_IMAGES` | Yes | R2 bucket for images |
| `DJANGO_ENV` | No | `local`, `development`, `test`, `ci`, `production` |
| `MODAL_CV_ENDPOINT` | No | Modal.com inference endpoint |
| `MODAL_AUTH_TOKEN` | No | Modal.com auth token |
| `MODEL_VERSION` | No | Model version (default: v0) |
| `DETECTION_CONFIDENCE_THRESHOLD` | No | Min confidence (default: 0.5) |

## License

Proprietary - All rights reserved.
