from __future__ import annotations
import httpx
from typing import Any, Dict, Optional

from backend.app.cache import cache
from backend.app.config import DEMO_MODE, OPENMETEO_BASE_URL
from backend.app.demo_data import get_demo_location


def fetch_json(url: str, params: Optional[Dict[str, Any]] = None, timeout: int = 20):
    response = httpx.get(url, params=params, timeout=timeout)
    response.raise_for_status()
    return response.json()


def cached_json(key: str, fetcher, ttl: int = 180, *args, **kwargs):
    cached = cache.get(key)
    if cached is not None:
        return cached
    result = fetcher(*args, **kwargs)
    cache.set(key, result, ttl_seconds=ttl)
    return result


from backend.app.services.base import cached_json, fetch_json
