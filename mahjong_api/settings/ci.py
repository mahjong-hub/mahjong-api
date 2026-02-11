"""
Used for fast CI jobs (linting, migration checks) without database.
Uses SQLite in-memory.
"""

from .base import *  # noqa: F401, F403

DEBUG = True

SECRET_KEY = 'ci-secret-key-not-for-production'

ALLOWED_HOSTS = ['*']

CSRF_TRUSTED_ORIGINS = []

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    },
}

DETECTION_CONFIDENCE_THRESHOLD = 0.5
