from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


class SimpleCache:
    """Simple in-memory TTL cache."""

    def __init__(self):
        self.data = {}

    def get(self, key: str) -> Optional[Any]:
        if key in self.data:
            value, expires = self.data[key]
            if datetime.now(timezone.utc) < expires:
                return value
            del self.data[key]
        return None

    def set(self, key: str, value: Any, ttl_seconds: int = 300):
        expires = datetime.now(timezone.utc).timestamp() + ttl_seconds
        self.data[key] = (value, datetime.fromtimestamp(expires, tz=timezone.utc))

    def clear(self):
        self.data.clear()


cache = SimpleCache()
