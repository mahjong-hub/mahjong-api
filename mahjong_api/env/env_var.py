from typing import Generic, TypeVar
import os
from pathlib import Path
from typing import Any

T = TypeVar('T')


class EnvVar(Generic[T]):
    def __init__(
        self,
        key: str,
        *,
        default: T | None = None,
        required: bool = False,
        secret: bool = False,
        description: str = '',
        group: str = 'Other',
        min_value: float | None = None,
        max_value: float | None = None,
        choices: list[T] | None = None,
    ):
        self.key = key
        self.default = default
        self.required = required
        self.secret = secret
        self.description = description
        self.group = group
        self.min_value = min_value
        self.max_value = max_value
        self.choices = choices
        self._cache_attr = f'_cache_{key}'

    def __set_name__(self, owner, name):
        self.attr_name = name

    def __get__(self, obj: Any, objtype=None) -> T:
        if obj is None:
            return self  # type: ignore

        # Check cache
        cached = getattr(obj, self._cache_attr, None)
        if cached is not None:
            return cached

        # Get raw value
        raw_value = os.getenv(self.key)

        # Handle missing/empty
        if raw_value is None or raw_value == '':
            if self.required and not obj._is_test:
                raise ValueError(
                    f"Required environment variable '{self.key}' is not set. "
                    f'{self.description}',
                )
            value = self.default
        else:
            value = self._convert(raw_value)

        # Validate
        self._validate(value)

        # Cache
        setattr(obj, self._cache_attr, value)
        return value  # type: ignore

    def _convert(self, raw_value: str) -> T:
        """Convert based on default value's type."""
        if self.default is None:
            return raw_value  # type: ignore

        if isinstance(self.default, bool):
            return raw_value.lower() in ('true', 'yes', '1', 'on')  # type: ignore
        elif isinstance(self.default, int):
            return int(raw_value)  # type: ignore
        elif isinstance(self.default, float):
            return float(raw_value)  # type: ignore
        elif isinstance(self.default, list):
            return [x.strip() for x in raw_value.split(',') if x.strip()]  # type: ignore
        elif isinstance(self.default, Path):
            return Path(raw_value).expanduser().resolve()  # type: ignore
        else:
            return raw_value  # type: ignore

    def _validate(self, value: T) -> None:
        """Validate value."""
        if value is None:
            return

        if self.min_value is not None and value < self.min_value:  # type: ignore
            raise ValueError(f"'{self.key}' must be >= {self.min_value}")

        if self.max_value is not None and value > self.max_value:  # type: ignore
            raise ValueError(f"'{self.key}' must be <= {self.max_value}")

        if self.choices and value not in self.choices:
            raise ValueError(f"'{self.key}' must be one of {self.choices}")

    def format_value(self, value: T) -> str:
        """Format for printing."""
        if value is None or value == '':
            return '(not set)'

        if self.secret:
            return '***hidden***' if value else '(not set)'

        if isinstance(value, list):
            if len(value) == 0:
                return '[]'
            if len(value) <= 3:
                return str(value)
            return f'[{len(value)} items]'

        if isinstance(value, str) and len(value) > 60:
            return f'{value[:57]}...'

        return str(value)
