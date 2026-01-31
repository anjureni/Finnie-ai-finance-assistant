# src/utils/cache.py
from datetime import datetime, timedelta
from typing import Any, Optional

def is_fresh(fetched_at: Optional[datetime], ttl_minutes: int) -> bool:
    if fetched_at is None:
        return False
    return datetime.now() - fetched_at < timedelta(minutes=ttl_minutes)

def mins_ago(fetched_at: Optional[datetime]) -> Optional[int]:
    if fetched_at is None:
        return None
    return int((datetime.now() - fetched_at).total_seconds() // 60)

class TTLCache:
    """
    Simple in-memory TTL cache.
    Store any python object with a fetched_at timestamp.
    """
    def __init__(self):
        self._store: dict[str, dict[str, Any]] = {}

    def get(self, key: str) -> Optional[dict[str, Any]]:
        return self._store.get(key)

    def set(self, key: str, value: Any):
        self._store[key] = {"value": value, "fetched_at": datetime.now()}
