"""
Django settings module.
"""

from mahjong_api.env import env


# Import all settings from the appropriate module
_settings_module = f'mahjong_api.settings.{env.environment}'

if _settings_module == 'mahjong_api.settings.production':
    from .production import *  # noqa: F401, F403
elif _settings_module == 'mahjong_api.settings.test':
    from .test import *  # noqa: F401, F403
elif _settings_module == 'mahjong_api.settings.ci':
    from .ci import *  # noqa: F401, F403
else:
    from .local import *  # noqa: F401, F403
