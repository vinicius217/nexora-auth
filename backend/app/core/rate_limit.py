from collections import defaultdict, deque
from threading import Lock
import time

from fastapi import HTTPException


class RateLimiter:
    def __init__(self, max_keys: int = 10_000):
        self._events: dict[str, deque[float]] = defaultdict(deque)
        self._max_keys = max_keys
        self._lock = Lock()

    def check(self, key: str, limit: int, window_seconds: int) -> None:
        now = time.monotonic()
        with self._lock:
            events = self._events[key]
            while events and events[0] <= now - window_seconds:
                events.popleft()
            if len(events) >= limit:
                retry = max(1, int(window_seconds - (now - events[0])))
                raise HTTPException(429, "Muitas tentativas. Tente novamente mais tarde.", headers={"Retry-After": str(retry)})
            events.append(now)
            if len(self._events) > self._max_keys:
                stale = [name for name, values in self._events.items() if not values or values[-1] <= now - window_seconds]
                for name in stale[: len(self._events) - self._max_keys]:
                    self._events.pop(name, None)


limiter = RateLimiter()
