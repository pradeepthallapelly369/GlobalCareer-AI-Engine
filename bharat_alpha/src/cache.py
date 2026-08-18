"""On-disk JSON cache for API responses.

The cache is keyed by a SHA1 of `(endpoint, params)` and stored as a
JSON file. Each file carries its `fetched_at` timestamp so the caller
can decide whether to refresh.
"""
from __future__ import annotations

import hashlib
import json
import math
import time
from pathlib import Path
from typing import Any, Optional


def _to_json_safe(obj: Any) -> Any:
    """Recursively convert numpy/pandas/NaN values into JSON-safe primitives."""
    if obj is None:
        return None
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    if isinstance(obj, (int, str, bool)):
        return obj
    if isinstance(obj, dict):
        return {str(k): _to_json_safe(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_to_json_safe(v) for v in obj]
    # Fallback: stringify
    return str(obj)


def cache_key(endpoint: str, params: dict) -> str:
    """Stable SHA1 hash for an (endpoint, params) pair."""
    payload = json.dumps({"endpoint": endpoint, "params": params}, sort_keys=True, default=str)
    return hashlib.sha1(payload.encode("utf-8")).hexdigest()


def _path_for(cache_dir: Path, key: str) -> Path:
    return cache_dir / f"{key}.json"


def read(key: str, cache_dir: Path, max_age_hours: int = 24) -> Optional[dict]:
    """Return cached payload if present and fresh, else None."""
    path = _path_for(cache_dir, key)
    if not path.exists():
        return None
    try:
        with path.open("r", encoding="utf-8") as fh:
            payload = json.load(fh)
    except (OSError, json.JSONDecodeError):
        return None
    fetched_at = payload.get("fetched_at", 0)
    age_hours = (time.time() - fetched_at) / 3600
    if age_hours > max_age_hours:
        return None
    return payload.get("data")


def write(key: str, data: Any, cache_dir: Path) -> None:
    """Write a payload to the cache, tagged with the current time."""
    cache_dir.mkdir(parents=True, exist_ok=True)
    path = _path_for(cache_dir, key)
    payload = {
        "fetched_at": time.time(),
        "data": _to_json_safe(data),
    }
    tmp = path.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, default=str)
    tmp.replace(path)


def is_fresh(key: str, cache_dir: Path, max_age_hours: int = 24) -> bool:
    """Return True if the cached entry exists and is within the freshness window."""
    return read(key, cache_dir, max_age_hours) is not None
