"""
Development settings for mahjong_api project.

Deployed on Render (dev instance) with Neon PostgreSQL and Cloudflare R2 storage.
Similar to production but with DEBUG=True and relaxed settings.
"""

from .base import *  # noqa: F401, F403
from mahjong_api.env import env
import dj_database_url
import logging

logger = logging.getLogger(__name__)

DEBUG = True

SECRET_KEY = env.secret_key

ALLOWED_HOSTS = env.allowed_hosts

if env.csrf_trusted_origins:
    CSRF_TRUSTED_ORIGINS = env.csrf_trusted_origins

# Database - Neon PostgreSQL via DATABASE_URL
if env.database_url:
    DATABASES = {
        'default': dj_database_url.config(
            default=env.database_url,
            conn_max_age=0,
            conn_health_checks=True,
            ssl_require=True,
        ),
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',  # noqa: F405
        },
    }

# Cloudflare R2 Storage
if env.r2_endpoint_url and env.r2_access_key_id:
    logger.info('Using Cloudflare R2 for media storage')
    STORAGE_BUCKET_IMAGES = env.r2_bucket_images

    MEDIA_URL = f'{env.r2_endpoint_url}/{env.r2_bucket_images}/'

    STORAGES = {
        'default': {
            'BACKEND': 'storages.backends.s3.S3Storage',
            'OPTIONS': {
                'access_key': env.r2_access_key_id,
                'secret_key': env.r2_secret_access_key,
                'bucket_name': env.r2_bucket_images,
                'endpoint_url': env.r2_endpoint_url,
                'region_name': 'auto',
                'signature_version': 's3v4',
                'addressing_style': 'auto',
                'file_overwrite': False,
                'default_acl': None,
                'querystring_auth': True,
                'querystring_expire': 3600,
            },
        },
        'staticfiles': {
            'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
        },
    }

    if env.r2_custom_domain:
        MEDIA_URL = f'https://{env.r2_custom_domain}/'
else:
    logger.warning('R2 credentials not configured, using local file storage')

# Celery
CELERY_BROKER_URL = env.celery_broker_url
CELERY_RESULT_BACKEND = env.celery_result_backend
CELERY_TASK_DEFAULT_QUEUE = env.celery_task_default_queue

# Detection settings
DETECTION_CONFIDENCE_THRESHOLD = env.detection_confidence_threshold

# Modal.com settings (if using)
if env.modal_cv_endpoint and env.model_version:
    MODAL_CV_ENDPOINT = env.modal_cv_endpoint
    MODEL_VERSION = env.model_version

# Logging - more verbose than production
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
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
        'level': 'DEBUG',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
        'storages': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
