import time
from collections import defaultdict, deque
from typing import Deque

from config import RATE_LIMIT_REQUESTS, RATE_LIMIT_WINDOW_SECONDS


class InMemoryRateLimiter:
    def __init__(self, max_requests: int, window_seconds: int) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: dict[str, Deque[float]] = defaultdict(deque)

    def _prune(self, key: str, now: float) -> None:
        window_start = now - self.window_seconds
        dq = self._requests[key]
        while dq and dq[0] < window_start:
            dq.popleft()

    def check_and_increment(self, key: str) -> bool:
        """
        Returns True if request is allowed, False if rate limit exceeded.
        """
        now = time.time()
        self._prune(key, now)
        dq = self._requests[key]
        if len(dq) >= self.max_requests:
            return False
        dq.append(now)
        return True

    def reset(self, *, max_requests: int | None = None, window_seconds: int | None = None) -> None:
        self._requests.clear()
        if max_requests is not None:
            self.max_requests = max_requests
        if window_seconds is not None:
            self.window_seconds = window_seconds


rate_limiter = InMemoryRateLimiter(
    max_requests=RATE_LIMIT_REQUESTS,
    window_seconds=RATE_LIMIT_WINDOW_SECONDS,
)
