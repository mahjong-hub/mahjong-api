from .base import *  # noqa: F401, F403

from mahjong_api.env import env
import dj_database_url

DEBUG = True if env.debug else False

SECRET_KEY = env.secret_key

ALLOWED_HOSTS = env.allowed_hosts

CSRF_TRUSTED_ORIGINS = env.csrf_trusted_origins

DATABASES = {
    'default': dj_database_url.config(
        default=env.database_url,
        conn_max_age=0,  # Don't persist connections in development
    ),
}

CELERY_BROKER_URL = env.celery_broker_url
CELERY_RESULT_BACKEND = env.celery_result_backend
CELERY_TASK_DEFAULT_QUEUE = env.celery_task_default_queue

DETECTION_CONFIDENCE_THRESHOLD = env.detection_confidence_threshold


STORAGE_BUCKET_IMAGES = env.r2_bucket_images
STORAGES = {
    'default': {
        'BACKEND': 'storages.backends.s3.S3Storage',
        'OPTIONS': {
            'access_key': env.r2_access_key_id,
            'secret_key': env.r2_secret_access_key,
            'bucket_name': STORAGE_BUCKET_IMAGES,
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
MEDIA_URL = f'{R2_ENDPOINT_URL}/{STORAGE_BUCKET_IMAGES}/'  # noqa: F405
