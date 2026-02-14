"""
Test settings for mahjong_api project.

Uses testcontainers for PostgreSQL to match production environment.
Automatically detected when running `python manage.py test`.
"""

import atexit

from testcontainers.postgres import PostgresContainer

from .base import *  # noqa: F401, F403

DEBUG = True

SECRET_KEY = 'test-secret-key-not-for-production'

ALLOWED_HOSTS = ['*']

CSRF_TRUSTED_ORIGINS = []

_postgres = PostgresContainer('postgres:16-alpine')
_postgres.start()

atexit.register(_postgres.stop)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': _postgres.dbname,
        'USER': _postgres.username,
        'PASSWORD': _postgres.password,
        'HOST': _postgres.get_container_host_ip(),
        'PORT': _postgres.get_exposed_port(5432),
    },
}

# Faster password hashing in tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

R2_ACCESS_KEY_ID = 'test-access-key-id'
R2_SECRET_ACCESS_KEY = 'test-secret-access-key'
R2_BUCKET_IMAGES = 'test-bucket-images'
R2_ENDPOINT_URL = 'http://invalid-endpoint-for-tests'

MODAL_CV_ENDPOINT = 'http://invalid-endpoint-for-tests'
MODAL_AUTH_TOKEN = 'test-token'
MODEL_VERSION = 'v0'

DETECTION_CONFIDENCE_THRESHOLD = 0.5
