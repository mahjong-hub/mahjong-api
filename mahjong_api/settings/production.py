from .base import *  # noqa: F401, F403

from mahjong_api.env import env
import logging
import dj_database_url

logger = logging.getLogger(__name__)

DEBUG = env.debug

SECRET_KEY = env.secret_key

ALLOWED_HOSTS = env.allowed_hosts


CSRF_TRUSTED_ORIGINS = env.csrf_trusted_origins

DATABASES = {
    'default': dj_database_url.config(
        default=env.database_url,
        conn_max_age=600,
        conn_health_checks=True,
        ssl_require=True,
    ),
}

# R2 is configured
logger.info('Using Cloudflare R2 for media storage')
STORAGE_BUCKET_IMAGES = env.r2_bucket_images

# Override MEDIA_URL
MEDIA_URL = f'{R2_ENDPOINT_URL}/{env.r2_bucket_images}/'  # noqa: F405

# Override storage backend
STORAGES = {
    'default': {
        'BACKEND': 'storages.backends.s3.S3Storage',
        'OPTIONS': {
            'access_key': env.r2_access_key_id,
            'secret_key': env.r2_secret_access_key,
            'bucket_name': env.r2_bucket_images,
            'endpoint_url': R2_ENDPOINT_URL,  # noqa: F405
            'region_name': 'auto',
            'signature_version': 's3v4',
            'addressing_style': 'auto',
            'file_overwrite': False,
            'default_acl': None,
            'querystring_auth': True,
            'querystring_expire': 3600,  # Signed URLs valid for 1 hour
            'object_parameters': {
                'CacheControl': 'max-age=86400',  # Cache media files for 1 day
            },
            'custom_domain': env.r2_custom_domain
            if env.r2_custom_domain
            else None,
        },
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}


CELERY_BROKER_URL = env.celery_broker_url
CELERY_RESULT_BACKEND = env.celery_result_backend
CELERY_TASK_DEFAULT_QUEUE = env.celery_task_default_queue

DETECTION_CONFIDENCE_THRESHOLD = env.detection_confidence_threshold

if env.modal_cv_endpoint and env.model_version:
    MODAL_CV_ENDPOINT = env.modal_cv_endpoint
    MODEL_VERSION = env.model_version

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
