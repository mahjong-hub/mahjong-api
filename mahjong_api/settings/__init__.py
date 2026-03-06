"""
Django settings module.
"""

from mahjong_api.env import env

if env.environment == 'production':
    from .production import *  # noqa: F401, F403
elif env.environment == 'development':
    from .development import *  # noqa: F401, F403
elif env.environment == 'test':
    from .test import *  # noqa: F401, F403
elif env.environment == 'ci':
    from .ci import *  # noqa: F401, F403
else:
    from .local import *  # noqa: F401, F403
