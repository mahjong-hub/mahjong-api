from .base import *  # noqa: F401, F403

from mahjong_api.env import env
import logging
import dj_database_url

logger = logging.getLogger(__name__)

DEBUG = env.DJANGO_DEBUG

SECRET_KEY = env.DJANGO_SECRET_KEY

ALLOWED_HOSTS = env.DJANGO_ALLOWED_HOSTS

CSRF_TRUSTED_ORIGINS = env.DJANGO_CSRF_TRUSTED_ORIGINS

DATABASES = {
    'default': dj_database_url.config(
        default=env.DATABASE_URL,
        conn_max_age=600,
        conn_health_checks=True,
        ssl_require=True,
    ),
}

STORAGE_BUCKET_IMAGES = env.R2_BUCKET_IMAGES

# Override MEDIA_URL
MEDIA_URL = f'{R2_ENDPOINT_URL}/{env.R2_BUCKET_IMAGES}/'  # noqa: F405
# Override storage backend
STORAGES = {
    'default': {
        'BACKEND': 'storages.backends.s3.S3Storage',
        'OPTIONS': {
            'access_key': env.AWS_ACCESS_KEY_ID,
            'secret_key': env.AWS_SECRET_ACCESS_KEY,
            'bucket_name': env.R2_BUCKET_IMAGES,
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
            'custom_domain': env.R2_CUSTOM_DOMAIN,
        },
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}

DETECTION_CONFIDENCE_THRESHOLD = env.DETECTION_CONFIDENCE_THRESHOLD

MODAL_CV_ENDPOINT = env.MODAL_CV_ENDPOINT
MODEL_VERSION = env.MODEL_VERSION

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
