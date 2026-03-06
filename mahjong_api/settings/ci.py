"""
Used for CI jobs (migration checks, linting, deploy migrations).
Requires psqlextra.backend — uses DATABASE_URL if set, otherwise
connects to the local CI postgres service container.
"""

import os

import dj_database_url

from .base import *  # noqa: F401, F403

DEBUG = True

SECRET_KEY = 'ci-secret-key-not-for-production'

ALLOWED_HOSTS = ['*']

CSRF_TRUSTED_ORIGINS = []

_default_db_url = 'postgresql://postgres:postgres@localhost:5432/mahjong_ci'

DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv('DATABASE_URL', _default_db_url),
        conn_max_age=0,
        ssl_require=bool(os.getenv('DATABASE_URL')),
        engine='psqlextra.backend',
    ),
}

DETECTION_CONFIDENCE_THRESHOLD = 0.5
