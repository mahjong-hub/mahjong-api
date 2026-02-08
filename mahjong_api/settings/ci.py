"""
CI settings for mahjong_api project.

Used for fast CI jobs (linting, migration checks) without database.
Uses SQLite in-memory.
"""

from .base import *  # noqa: F401, F403

DEBUG = True

SECRET_KEY = 'ci-secret-key-not-for-production'

ALLOWED_HOSTS = ['*']

CSRF_TRUSTED_ORIGINS = []

# Database - SQLite in-memory for fast CI
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    },
}

# Celery - disabled for CI
CELERY_BROKER_URL = 'memory://'
CELERY_RESULT_BACKEND = 'cache+memory://'
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
CELERY_TASK_DEFAULT_QUEUE = 'ci-queue'

# Storage - local filesystem for CI
# (STORAGES already defined in base.py with local storage)

# Detection settings
DETECTION_CONFIDENCE_THRESHOLD = 0.5
