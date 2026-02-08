"""
Production settings for mahjong_api project.

Deployed on Render with Neon PostgreSQL and Cloudflare R2 storage.
"""

from .base import *  # noqa: F401, F403
from mahjong_api.env import env
import logging

logger = logging.getLogger(__name__)

DEBUG = env.debug

SECRET_KEY = env.secret_key

ALLOWED_HOSTS = env.allowed_hosts

if env.csrf_trusted_origins:
    CSRF_TRUSTED_ORIGINS = env.csrf_trusted_origins

# Database - Neon PostgreSQL via DATABASE_URL
if env.database_url:
    import dj_database_url

    DATABASES = {
        'default': dj_database_url.config(
            default=env.database_url,
            conn_max_age=600,
            conn_health_checks=True,
            ssl_require=True,
        ),
    }
else:
    # Fallback to Render's auto-provided env vars
    import os

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('PGDATABASE'),
            'USER': os.environ.get('PGUSER'),
            'PASSWORD': os.environ.get('PGPASSWORD'),
            'HOST': os.environ.get('PGHOST'),
            'PORT': os.environ.get('PGPORT', '5432'),
            'OPTIONS': {
                'sslmode': 'require',
            },
            'CONN_MAX_AGE': 600,
        },
    }

# Cloudflare R2 Storage - Django 4.2+ OPTIONS style
if env.r2_endpoint_url and env.r2_access_key_id:
    # R2 is configured
    logger.info('Using Cloudflare R2 for media storage')

    # Override MEDIA_URL
    MEDIA_URL = f'{env.r2_endpoint_url}/{env.r2_bucket_images}/'

    # Override storage backend
    STORAGES = {
        'default': {
            'BACKEND': 'storages.backends.s3.S3Storage',
            'OPTIONS': {
                # Authentication
                'access_key': env.r2_access_key_id,
                'secret_key': env.r2_secret_access_key,
                'bucket_name': env.r2_bucket_images,
                'endpoint_url': env.r2_endpoint_url,
                # R2-specific settings
                'region_name': 'auto',
                'signature_version': 's3v4',
                'addressing_style': 'auto',
                # File handling
                'file_overwrite': False,
                'default_acl': None,
                'querystring_auth': True,
                'querystring_expire': 3600,
                # Performance
                'object_parameters': {
                    'CacheControl': 'max-age=86400',
                },
                # Custom domain (optional)
                'custom_domain': env.r2_custom_domain
                if env.r2_custom_domain
                else None,
            },
        },
        'staticfiles': {
            'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
        },
    }

    # Update MEDIA_URL if custom domain is set
    if env.r2_custom_domain:
        MEDIA_URL = f'https://{env.r2_custom_domain}/'
else:
    # R2 not configured - fallback to local storage (shouldn't happen in prod)
    logger.warning('R2 credentials not configured, using local file storage')

# Celery - Render Redis
CELERY_BROKER_URL = env.celery_broker_url
CELERY_RESULT_BACKEND = env.celery_result_backend
CELERY_TASK_DEFAULT_QUEUE = env.celery_task_default_queue

# Detection settings
DETECTION_CONFIDENCE_THRESHOLD = env.detection_confidence_threshold

# Modal.com settings (if using)
if env.modal_cv_endpoint and env.model_version:
    MODAL_CV_ENDPOINT = env.modal_cv_endpoint
    MODEL_VERSION = env.model_version

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} '
            '{message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'storages': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
