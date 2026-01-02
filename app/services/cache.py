import time
from typing import Any, Optional


class TTLCache:
    def __init__(self, ttl_seconds: int, max_items: int = 256) -> None:
        self._ttl_seconds = ttl_seconds
        self._max_items = max_items
        self._store: dict[object, tuple[float, Any]] = {}

    def get(self, key: object) -> Optional[Any]:
        item = self._store.get(key)
        if not item:
            return None

        expires_at, value = item
        if expires_at <= time.monotonic():
            self._store.pop(key, None)
            return None

        return value

    def set(self, key: object, value: Any) -> None:
        if len(self._store) >= self._max_items:
            self._store.pop(next(iter(self._store)), None)

        self._store[key] = (time.monotonic() + self._ttl_seconds, value)
