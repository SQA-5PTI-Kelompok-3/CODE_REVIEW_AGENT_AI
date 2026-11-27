"""Thread-safe in-memory cache with hit counters."""
import threading


class Cache:
    def __init__(self):
        self._data = {}
        self._hits = 0
        self._lock = threading.Lock()

    def get(self, key):
        with self._lock:
            if key in self._data:
                self._hits += 1
                return self._data[key]
            return None

    def get_or_compute(self, key, compute):
        if key not in self._data:
            self._data[key] = compute()
        self._hits += 1
        return self._data[key]

    def clear(self):
        with self._lock:
            self._data.clear()
