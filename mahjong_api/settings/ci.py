"""
Used for CI jobs. Uses SQLite in-memory by default,
or a real database if DATABASE_URL is set (for migrations).
"""

import os

from .base import *  # noqa: F401, F403

DEBUG = True

SECRET_KEY = 'ci-secret-key-not-for-production'

ALLOWED_HOSTS = ['*']

CSRF_TRUSTED_ORIGINS = []

if os.getenv('DATABASE_URL'):
    import dj_database_url

    DATABASES = {
        'default': dj_database_url.config(
            conn_max_age=0,
            ssl_require=True,
        ),
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        },
    }

DETECTION_CONFIDENCE_THRESHOLD = 0.5
