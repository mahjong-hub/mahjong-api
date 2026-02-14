import sys
from .env_var import EnvVar


class EnvConfig:
    DJANGO_ENV: str = EnvVar(
        'DJANGO_ENV',
        default='local',
        choices=['local', 'development', 'test', 'ci', 'production'],
        description='Application environment',
        group='Environment',
    )

    DJANGO_SECRET_KEY: str = EnvVar(
        'DJANGO_SECRET_KEY',
        required=True,
        secret=True,
        description='Django secret key',
        group='Django',
    )

    DJANGO_DEBUG: bool = EnvVar(
        'DJANGO_DEBUG',
        default=True,
        description='Django debug mode',
        group='Django',
    )

    DJANGO_ALLOWED_HOSTS: list[str] = EnvVar(
        'DJANGO_ALLOWED_HOSTS',
        default=['localhost', '127.0.0.1'],
        description='Allowed hosts',
        group='Django',
    )

    DJANGO_CSRF_TRUSTED_ORIGINS: list[str] = EnvVar(
        'DJANGO_CSRF_TRUSTED_ORIGINS',
        default=[],
        description='CSRF trusted origins',
        group='Django',
    )

    DATABASE_URL: str = EnvVar(
        'DATABASE_URL',
        required=True,
        secret=True,
        description='PostgreSQL connection string',
        group='Database',
    )

    AWS_ACCESS_KEY_ID: str = EnvVar(
        'AWS_ACCESS_KEY_ID',
        required=True,
        secret=True,
        description='AWS access key ID',
        group='Storage',
    )

    AWS_SECRET_ACCESS_KEY: str = EnvVar(
        'AWS_SECRET_ACCESS_KEY',
        required=True,
        secret=True,
        description='AWS secret access key',
        group='Storage',
    )

    R2_ACCOUNT_ID: str = EnvVar(
        'R2_ACCOUNT_ID',
        required=True,
        description='R2 account ID',
        group='Storage',
    )

    R2_BUCKET_IMAGES: str = EnvVar(
        'R2_BUCKET_IMAGES',
        required=True,
        description='R2 bucket for images',
        group='Storage',
    )

    R2_CUSTOM_DOMAIN: str | None = EnvVar(
        'R2_CUSTOM_DOMAIN',
        description='R2 custom domain',
        group='Storage',
    )

    MODAL_CV_ENDPOINT: str = EnvVar(
        'MODAL_CV_ENDPOINT',
        default='',
        description='Modal.com CV endpoint',
        group='ML/CV',
    )

    MODAL_AUTH_TOKEN: str = EnvVar(
        'MODAL_AUTH_TOKEN',
        default='',
        secret=True,
        description='Modal.com authentication token',
        group='ML/CV',
    )

    MODEL_VERSION: str = EnvVar(
        'MODEL_VERSION',
        default='v0',
        choices=['v0', 'v1', 'v2', 'v3'],
        description='Model version',
        group='ML/CV',
    )

    DETECTION_CONFIDENCE_THRESHOLD: float = EnvVar(
        'DETECTION_CONFIDENCE_THRESHOLD',
        default=0.5,
        min_value=0.0,
        max_value=1.0,
        description='Detection confidence threshold',
        group='ML/CV',
    )

    @property
    def _is_test(self) -> bool:
        """Internal: check if running tests."""
        return 'test' in sys.argv or 'pytest' in sys.modules

    @property
    def is_test(self) -> bool:
        """Running in test mode."""
        return self.DJANGO_ENV == 'test' or self._is_test

    @property
    def is_ci(self) -> bool:
        """Running in CI."""
        return self.DJANGO_ENV == 'ci'

    @property
    def is_local(self) -> bool:
        """Running locally."""
        return self.DJANGO_ENV == 'local'

    @property
    def is_development(self) -> bool:
        """Running in development."""
        return self.DJANGO_ENV == 'development'

    @property
    def is_production(self) -> bool:
        """Running in production."""
        return self.DJANGO_ENV == 'production'

    @property
    def environment(self) -> str:
        """Current environment name."""
        return self.DJANGO_ENV

    @property
    def r2_endpoint_url(self) -> str:
        """R2 endpoint URL constructed from account ID."""
        if not self.R2_ACCOUNT_ID:
            return ''
        return f'https://{self.R2_ACCOUNT_ID}.r2.cloudflarestorage.com'

    @property
    def has_r2(self) -> bool:
        """Check if R2 is fully configured."""
        return bool(
            self.R2_ACCOUNT_ID
            and self.AWS_ACCESS_KEY_ID
            and self.AWS_SECRET_ACCESS_KEY,
        )

    @property
    def has_modal(self) -> bool:
        """Check if Modal.com is configured."""
        return bool(self.MODAL_CV_ENDPOINT)

    def print_config(self, show_secrets: bool = False) -> None:
        """Print all environment variables grouped by category."""
        # Collect all EnvVar descriptors
        env_vars: dict[str, tuple[str, EnvVar]] = {}

        for name in dir(self.__class__):
            if name.startswith('_'):
                continue

            attr = getattr(self.__class__, name)
            if isinstance(attr, EnvVar):
                env_vars[name] = (name, attr)

        # Group by category
        groups: dict[str, list[tuple[str, EnvVar]]] = {}
        for _, (prop_name, env_var) in env_vars.items():
            group = env_var.group
            if group not in groups:
                groups[group] = []
            groups[group].append((prop_name, env_var))

        # Print header
        print(f'\n{"=" * 70}')
        print(f'Environment Configuration ({self.environment})')
        print(f'{"=" * 70}')

        # Print each group
        for group_name in sorted(groups.keys()):
            print(f'\n[{group_name}]')

            for prop_name, env_var in sorted(groups[group_name]):
                value = getattr(self, prop_name)

                # Format value
                if show_secrets:
                    formatted = (
                        str(value) if value is not None else '(not set)'
                    )
                else:
                    formatted = env_var.format_value(value)

                print(f'  {prop_name:30} = {formatted}')

                if env_var.description:
                    print(f'    └─ {env_var.description}')

        print('\n[Features]')
        print(
            f'  R2 Storage:   {
                "✓ Configured" if self.has_r2 else "✗ Not configured"
            }',
        )
        print(
            f'  Modal.com:    {
                "✓ Configured" if self.has_modal else "✗ Not configured"
            }',
        )

        print(f'\n{"=" * 70}\n')

    def validate(self) -> list[str]:
        """Validate all required env vars are set."""
        errors = []

        for name in dir(self.__class__):
            if name.startswith('_'):
                continue

            attr = getattr(self.__class__, name)
            if isinstance(attr, EnvVar):
                if attr.required and not (self._is_test or self.is_ci):
                    value = getattr(self, name, None)
                    if not value:
                        errors.append(
                            f'Required: {attr.key} ({attr.description or name})',
                        )

        return errors
