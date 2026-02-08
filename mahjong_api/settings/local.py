"""
Local development settings for mahjong_api project.

Uses local PostgreSQL or SQLite for development.
Storage defaults to local filesystem.
"""

from .base import *  # noqa: F401, F403
from mahjong_api.env import env
import dj_database_url

DEBUG = True if env.debug else False

SECRET_KEY = env.secret_key

ALLOWED_HOSTS = env.allowed_hosts

if env.csrf_trusted_origins:
    CSRF_TRUSTED_ORIGINS = env.csrf_trusted_origins

if env.database_url:
    DATABASES = {
        'default': dj_database_url.config(
            default=env.database_url,
            conn_max_age=0,  # Don't persist connections in development
        ),
    }
else:
    # Fallback to SQLite
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',  # noqa: F405
        },
    }

# Celery
CELERY_BROKER_URL = env.celery_broker_url
CELERY_RESULT_BACKEND = env.celery_result_backend
CELERY_TASK_DEFAULT_QUEUE = env.celery_task_default_queue

# Storage
# (Using base.py defaults - local file storage)

# Detection settings
DETECTION_CONFIDENCE_THRESHOLD = env.detection_confidence_threshold

if env.r2_endpoint_url and env.r2_access_key_id:
    R2_BUCKET_IMAGES = 'mahjong-api-images-dev'
    STORAGES = {
        'default': {
            'BACKEND': 'storages.backends.s3.S3Storage',
            'OPTIONS': {
                'access_key': env.r2_access_key_id,
                'secret_key': env.r2_secret_access_key,
                'bucket_name': R2_BUCKET_IMAGES,
                'endpoint_url': env.r2_endpoint_url,
                'region_name': 'auto',
                'signature_version': 's3v4',
                'addressing_style': 'auto',
                'file_overwrite': False,
                'default_acl': None,
            },
        },
        'staticfiles': {
            'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
        },
    }
    MEDIA_URL = f'{env.r2_endpoint_url}/{R2_BUCKET_IMAGES}/'
