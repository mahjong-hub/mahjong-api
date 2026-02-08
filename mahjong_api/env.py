"""
Environment variable management for mahjong_api project.

Features:
- Type-safe getters (string, int, float, bool, list)
- Validation with helpful error messages
- Environment-aware defaults (test/dev/prod)
- Auto-documentation of required variables
- Graceful degradation for optional features
"""

import os
import sys
import logging
from pathlib import Path

from dotenv import load_dotenv

logger = logging.getLogger(__name__)

load_dotenv()


class BaseEnvConfig:
    """Environment configuration manager with type-safe getters."""

    def __init__(self):
        self._env = os.environ.copy()
        self._missing_required = []

    # ============================================
    # Type-Safe Getters
    # ============================================

    def get_str(
        self,
        key: str,
        default: str | None = None,
        required: bool = False,
        description: str = None,
    ) -> str:
        """
        Get string environment variable.

        Args:
            key: Environment variable name
            default: Default value if not set
            required: Raise error if not set and no default
            description: Human-readable description for error messages
        """
        value = self._env.get(key)

        if value is None or value == '':
            if required and not self._is_test:
                desc = description or key
                self._missing_required.append(f'{key} ({desc})')
                raise ValueError(
                    f"Required environment variable '{key}' is not set. "
                    f'Description: {desc}',
                ) from None
            return default or ''

        return value

    def get_int(
        self,
        key: str,
        default: int | None = None,
        required: bool = False,
        min_value: int | None = None,
        max_value: int | None = None,
    ) -> int:
        """Get integer environment variable with optional validation."""
        value = self.get_str(
            key,
            str(default) if default is not None else None,
            required,
        )

        if not value:
            return default or 0

        try:
            int_value = int(value)
        except ValueError:
            raise ValueError(
                f"Environment variable '{key}' must be an integer, got: {value}",
            ) from None

        if min_value is not None and int_value < min_value:
            raise ValueError(
                f'{key} must be >= {min_value}, got: {int_value}',
            ) from None

        if max_value is not None and int_value > max_value:
            raise ValueError(
                f'{key} must be <= {max_value}, got: {int_value}',
            ) from None

        return int_value

    def get_float(
        self,
        key: str,
        default: float | None = None,
        required: bool = False,
        min_value: float | None = None,
        max_value: float | None = None,
    ) -> float:
        """Get float environment variable with optional validation."""
        value = self.get_str(
            key,
            str(default) if default is not None else None,
            required,
        )

        if not value:
            return default or 0.0

        try:
            float_value = float(value)
        except ValueError:
            raise ValueError(
                f"Environment variable '{key}' must be a float, got: {value}",
            ) from None

        if min_value is not None and float_value < min_value:
            raise ValueError(
                f'{key} must be >= {min_value}, got: {float_value}',
            ) from None

        if max_value is not None and float_value > max_value:
            raise ValueError(
                f'{key} must be <= {max_value}, got: {float_value}',
            ) from None

        return float_value

    def get_bool(self, key: str, default: bool = False) -> bool:
        """
        Get boolean environment variable.

        Accepts: true/false, yes/no, 1/0 (case-insensitive)
        """
        value = self.get_str(key, str(default))

        if not value:
            return default

        return value.lower() in ('true', 'yes', '1', 'on')

    def get_list(
        self,
        key: str,
        default: list[str] | None = None,
        separator: str = ',',
        strip: bool = True,
    ) -> list[str]:
        """
        Get list environment variable (comma-separated by default).

        Example: "foo,bar,baz" → ["foo", "bar", "baz"]
        """
        value = self.get_str(key, '')

        if not value:
            return default or []

        items = value.split(separator)

        if strip:
            items = [item.strip() for item in items if item.strip()]

        return items

    def get_path(
        self,
        key: str,
        default: str | None = None,
        must_exist: bool = False,
    ) -> Path:
        """Get path environment variable as Path object."""
        value = self.get_str(key, default)

        if not value:
            return Path('.')

        path = Path(value).expanduser().resolve()

        if must_exist and not path.exists():
            raise ValueError(
                f"Path for '{key}' does not exist: {path}",
            ) from None

        return path

    # ============================================
    # Feature Flags
    # ============================================

    def has_feature(self, feature_name: str) -> bool:
        """
        Check if a feature is enabled.

        Checks for FEATURE_<NAME>=true or <NAME>_ENABLED=true
        """
        # Check FEATURE_NAME
        if self.get_bool(f'FEATURE_{feature_name.upper()}'):
            return True

        # Check NAME_ENABLED
        if self.get_bool(f'{feature_name.upper()}_ENABLED'):
            return True

        return False

    # ============================================
    # Validation
    # ============================================

    def validate(self) -> None:
        """
        Validate all required environment variables are set.

        Raises ValueError if any required variables are missing.
        """
        if self._missing_required:
            missing = '\n  - '.join(self._missing_required)
            raise ValueError(
                f'Missing required environment variables:\n  - {missing}\n\n'
                f'Please set these in your .env file or environment.',
            ) from None

    def print_config(self) -> None:
        """Print current configuration (for debugging)."""
        print(f'\n{"=" * 60}')
        print(f'Environment Configuration ({self.environment})')
        print(f'{"=" * 60}')

        print('\n[Environment]')
        print(f'  Mode: {self.environment}')
        print(f'  Debug: {self.debug}')
        print(f'  Testing: {self.is_test}')
        print(f'  CI: {self.is_ci}')


class EnvConfig(BaseEnvConfig):
    def __init__(self):
        super().__init__()
        self._django_env = self.get_str(
            'DJANGO_ENV',
            default='',
            required=False,
        )
        self._is_test = (
            self._django_env == 'test'
            or 'test' in sys.argv
            or 'pytest' in sys.modules
        )
        self._is_ci = self._django_env == 'ci'
        self._is_production = self._django_env == 'production'
        self._is_local = self._django_env == 'local'

    # ============================================
    # Environment Detection
    # ============================================

    @property
    def is_test(self) -> bool:
        """Running in test mode (pytest, manage.py test)."""
        return self._is_test

    @property
    def is_ci(self) -> bool:
        """Running in CI environment (GitHub Actions, etc.)."""
        return self._is_ci

    @property
    def is_production(self) -> bool:
        """Running in production (not test, not CI, DEBUG=False)."""
        return self._is_production

    @property
    def environment(self) -> str:
        """Current environment: 'test', 'ci', 'local', or 'production'."""
        django_env = self.get_str('DJANGO_ENV', default='', required=False)
        if django_env:
            return django_env.lower()
        if self._is_test:
            return 'test'
        if self._is_ci:
            return 'ci'
        if self._is_local:
            return 'local'
        return 'production'

    # ============================================
    # Django Settings
    # ============================================

    @property
    def secret_key(self) -> str:
        """Django SECRET_KEY."""
        return self.get_str(
            'DJANGO_SECRET_KEY',
            default='dev-secret-key-change-in-production',
            required=self.is_production,
            description='Django secret key for cryptographic signing',
        )

    @property
    def debug(self) -> bool:
        """Django DEBUG mode."""
        return self.get_bool('DJANGO_DEBUG', default=not self.is_production)

    @property
    def allowed_hosts(self) -> list[str]:
        """Django ALLOWED_HOSTS."""
        return self.get_list(
            'DJANGO_ALLOWED_HOSTS',
            default=['localhost', '127.0.0.1']
            if not self.is_production
            else [],
        )

    @property
    def csrf_trusted_origins(self) -> list[str]:
        """Django CSRF_TRUSTED_ORIGINS."""
        return self.get_list('DJANGO_CSRF_TRUSTED_ORIGINS', default=[])

    # ============================================
    # Database Settings
    # ============================================

    @property
    def database_url(self) -> str:
        """Database connection URL."""
        return self.get_str(
            'DATABASE_URL',
            default='',
            required=self.is_production,
            description='PostgreSQL database URL',
        )

    # ============================================
    # Cloudflare R2 Storage
    # ============================================

    @property
    def has_r2(self) -> bool:
        """Check if Cloudflare R2 storage is configured."""
        return bool(
            self.r2_endpoint_url
            and self.r2_access_key_id
            and self.r2_secret_access_key,
        )

    @property
    def r2_access_key_id(self) -> str:
        """R2 access key ID."""
        return self.get_str('R2_ACCESS_KEY_ID', default='')

    @property
    def r2_secret_access_key(self) -> str:
        """R2 secret access key."""
        return self.get_str('R2_SECRET_ACCESS_KEY', default='')

    @property
    def r2_endpoint_url(self) -> str:
        """R2 endpoint URL."""
        return self.get_str('R2_ENDPOINT_URL', default='')

    @property
    def r2_bucket_images(self) -> str:
        """R2 bucket for user-uploaded images."""
        return self.get_str('R2_BUCKET_IMAGES', default='')

    @property
    def r2_bucket_models(self) -> str:
        """R2 bucket for ML model weights."""
        return self.get_str('R2_BUCKET_MODELS', default='')

    @property
    def r2_custom_domain(self) -> str:
        """R2 custom domain (optional)."""
        return self.get_str('R2_CUSTOM_DOMAIN', default='')

    # ============================================
    # Celery Settings
    # ============================================

    @property
    def has_celery(self) -> bool:
        """Check if Celery is configured (requires broker and backend)."""
        return bool(self.celery_broker_url and self.celery_result_backend)

    @property
    def celery_broker_url(self) -> str:
        """Celery broker URL."""
        return self.get_str(
            'CELERY_BROKER_URL',
            default='redis://localhost:6379/0',
        )

    @property
    def celery_result_backend(self) -> str:
        """Celery result backend URL."""
        return self.get_str(
            'CELERY_RESULT_BACKEND',
            default='redis://localhost:6379/0',
        )

    @property
    def celery_task_default_queue(self) -> str:
        """Default Celery task queue name."""
        return self.get_str(
            'CELERY_TASK_DEFAULT_QUEUE',
            default='mahjong-default',
        )

    # ============================================
    # ML/CV Settings
    # ============================================

    @property
    def has_modal(self) -> bool:
        """Check if Modal.com CV endpoint is configured."""
        return bool(self.modal_cv_endpoint and self.model_version)

    @property
    def modal_cv_endpoint(self) -> str:
        """Modal.com CV detection endpoint URL."""
        return self.get_str('MODAL_CV_ENDPOINT', default='')

    @property
    def model_version(self) -> str:
        """ML model version to use (v1, v2, v3)."""
        return self.get_str('MODEL_VERSION', default='')

    @property
    def detection_confidence_threshold(self) -> float:
        """Minimum confidence threshold for tile detection (0.0-1.0)."""
        return self.get_float(
            'DETECTION_CONFIDENCE_THRESHOLD',
            default=0.5,
            min_value=0.0,
            max_value=1.0,
        )

    def print_config(self) -> None:
        """Print current configuration (for debugging)."""
        print(f'\n{"=" * 60}')
        print(f'Environment Configuration ({self.environment})')
        print(f'{"=" * 60}')

        print('\n[Environment]')
        print(f'  Mode: {self.environment}')
        print(f'  Debug: {self.debug}')
        print(f'  Testing: {self.is_test}')
        print(f'  CI: {self.is_ci}')

        print('\n[Django]')
        print(f'  Secret Key: {"*" * 20} (hidden)')
        print(f'  Allowed Hosts: {self.allowed_hosts}')
        csrf_origins_count = len(self.csrf_trusted_origins or [])
        print(f'  CSRF Origins: {csrf_origins_count} configured')

        print('\n[Database]')
        print(
            f'  URL: {self.database_url[:50]}...'
            if self.database_url
            else '  URL: (not set)',
        )

        print('\n[Storage]')
        print(f'  R2 Configured: {self.has_r2}')
        if self.has_r2:
            print(f'  R2 Endpoint: {self.r2_endpoint_url}')
            print(f'  R2 Images Bucket: {self.r2_bucket_images}')
            print(f'  R2 Models Bucket: {self.r2_bucket_models}')
            if self.r2_custom_domain:
                print(f'  R2 Custom Domain: {self.r2_custom_domain}')

        print('\n[Celery]')
        print(
            f'  Redis Configured: {self.celery_broker_url.startswith("redis://")}',
        )
        print(f'  Broker: {self.celery_broker_url[:50]}...')
        print(f'  Default Queue: {self.celery_task_default_queue}')

        print('\n[ML/CV]')
        print(f'  Modal Configured: {self.has_modal}')
        if self.has_modal:
            print(f'  Modal Endpoint: {self.modal_cv_endpoint[:50]}...')
        print(f'  Model Version: {self.model_version}')
        print(f'  Detection Threshold: {self.detection_confidence_threshold}')

        print(f'\n{"=" * 60}\n')


env = EnvConfig()

if env.is_production:
    try:
        env.validate()
    except ValueError as e:
        logger.error(f'Environment validation failed: {e}')
        # Don't raise in production startup, just log
        # Let the app start and fail gracefully when features are used
