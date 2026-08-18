"""Token-bucket rate limiter for the Alpha Vantage free tier (5 req/min).

Usage:
    bucket = TokenBucket(per_minute=5)
    bucket.wait()        # sleeps if needed
    ... make request ...
    bucket.record()      # log the call

The class is intentionally simple — it tracks timestamps of recent calls
in a deque and sleeps just enough before the next call to stay under
the limit.
"""
from __future__ import annotations

import time
from collections import deque
from threading import Lock
from typing import Deque


class TokenBucket:
    """Sleeps to enforce a per-minute request budget."""

    def __init__(self, per_minute: int = 5):
        if per_minute < 1:
            raise ValueError("per_minute must be >= 1")
        self.per_minute = per_minute
        self._calls: Deque[float] = deque()
        self._lock = Lock()

    def _prune(self, now: float) -> None:
        window_start = now - 60.0
        while self._calls and self._calls[0] < window_start:
            self._calls.popleft()

    def wait(self) -> None:
        """Block until making another call would not exceed the rate limit."""
        with self._lock:
            now = time.monotonic()
            self._prune(now)
            if len(self._calls) < self.per_minute:
                return
            # Sleep until the oldest call falls outside the 60s window
            sleep_for = 60.0 - (now - self._calls[0])
            if sleep_for > 0:
                time.sleep(sleep_for)

    def record(self) -> None:
        """Log that a call was just made."""
        with self._lock:
            self._calls.append(time.monotonic())

    def calls_in_last_minute(self) -> int:
        with self._lock:
            self._prune(time.monotonic())
            return len(self._calls)
