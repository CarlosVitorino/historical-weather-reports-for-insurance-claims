"""In-memory rate limits per client IP. Enough for one server process, which is how this app runs (see deploy/).

Each rule is (requests, seconds): a sliding window per IP. State is lost on restart, which only ever errs towards
letting people in. Behind the edge proxy, uvicorn's --proxy-headers makes request.client the real visitor.
"""
import threading
import time
from collections import deque

# path prefix → (max requests, window in seconds). The order form calls /api/suggest about once per pause in
# typing and /api/geocode once per address, so these leave a real buyer far below the limit.
RULES = {
    "POST /order": (10, 600),          # each one writes a row and calls the Census geocoder
    "GET /api/suggest": (120, 600),    # each one may cost a Geoapify request
    "GET /api/geocode": (30, 600),
    "GET /api/reverse": (60, 600),
    "POST /order/": (20, 600),         # checkout clicks: each one creates a creem checkout session
}


class Limiter:
    def __init__(self, rules: dict[str, tuple[int, int]] | None = None, clock=time.monotonic):
        self.rules = RULES if rules is None else rules
        self.clock = clock
        self._hits: dict[tuple[str, str], deque] = {}
        self._lock = threading.Lock()
        self._last_sweep = clock()

    def rule_for(self, method: str, path: str) -> str | None:
        key = f"{method} {path}"
        if key in self.rules:
            return key
        for rule in self.rules:   # prefix rules end in "/"
            if rule.endswith("/") and key.startswith(rule):
                return rule
        return None

    def allow(self, method: str, path: str, client: str) -> bool:
        rule = self.rule_for(method, path)
        if rule is None:
            return True
        limit, window = self.rules[rule]
        t = self.clock()
        with self._lock:
            q = self._hits.setdefault((rule, client), deque())
            while q and q[0] <= t - window:
                q.popleft()
            if len(q) >= limit:
                return False
            q.append(t)
            if t - self._last_sweep > 600:   # forget idle visitors so memory stays flat
                self._last_sweep = t
                for k in [k for k, v in self._hits.items() if not v or v[-1] <= t - 3600]:
                    del self._hits[k]
            return True


class DailyBudget:
    """A cap on calls to a paid or quota'd upstream per UTC day (thread-safe)."""

    def __init__(self, per_day: int, clock=time.time):
        self.per_day, self.clock = per_day, clock
        self._day, self._used = None, 0
        self._lock = threading.Lock()

    def take(self) -> bool:
        day = int(self.clock() // 86400)
        with self._lock:
            if day != self._day:
                self._day, self._used = day, 0
            if self._used >= self.per_day:
                return False
            self._used += 1
            return True
