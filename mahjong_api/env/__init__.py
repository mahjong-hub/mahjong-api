from .env_config import EnvConfig
import logging

logger = logging.getLogger(__name__)


env = EnvConfig()

if env.is_production:
    validation_errors = env.validate()
    if validation_errors:
        error_msg = '\n  - '.join(validation_errors)
        logger.error(f'Environment validation failed:\n  - {error_msg}')
