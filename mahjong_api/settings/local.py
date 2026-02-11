from .base import *  # noqa: F401, F403

from mahjong_api.env import env
import dj_database_url

DEBUG = env.DJANGO_DEBUG

SECRET_KEY = env.DJANGO_SECRET_KEY

ALLOWED_HOSTS = env.DJANGO_ALLOWED_HOSTS
CSRF_TRUSTED_ORIGINS = env.DJANGO_CSRF_TRUSTED_ORIGINS

DATABASES = {
    'default': dj_database_url.config(
        default=env.DATABASE_URL,
        conn_max_age=0,  # Don't persist connections
    ),
}

DETECTION_CONFIDENCE_THRESHOLD = env.DETECTION_CONFIDENCE_THRESHOLD

STORAGE_BUCKET_IMAGES = env.R2_BUCKET_IMAGES

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
        },
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}

MEDIA_URL = f'{R2_ENDPOINT_URL}/{env.R2_BUCKET_IMAGES}/'  # noqa: F405

MODAL_CV_ENDPOINT = env.MODAL_CV_ENDPOINT
MODEL_VERSION = env.MODEL_VERSION
