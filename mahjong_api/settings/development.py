from .base import *  # noqa: F401, F403

from mahjong_api.env import env
import dj_database_url
import logging

logger = logging.getLogger(__name__)

DEBUG = True

SECRET_KEY = env.DJANGO_SECRET_KEY

ALLOWED_HOSTS = env.DJANGO_ALLOWED_HOSTS

CSRF_TRUSTED_ORIGINS = env.DJANGO_CSRF_TRUSTED_ORIGINS

DATABASES = {
    'default': dj_database_url.config(
        default=env.DATABASE_URL,
        conn_max_age=0,
        conn_health_checks=True,
        ssl_require=True,
    ),
}

STORAGE_BUCKET_IMAGES = env.R2_BUCKET_IMAGES

MEDIA_URL = f'{R2_ENDPOINT_URL}/{env.R2_BUCKET_IMAGES}/'  # noqa: F405

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
            'querystring_expire': 3600,
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
