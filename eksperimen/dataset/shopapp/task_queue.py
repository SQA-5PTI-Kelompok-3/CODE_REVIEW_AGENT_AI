"""A small bounded FIFO queue used by background workers."""
from collections import deque
import threading


class TaskQueue:
    def __init__(self, maxsize):
        if maxsize <= 0:
            raise ValueError("maxsize must be positive")
        self._items = deque()
        self._maxsize = maxsize
        self._cond = threading.Condition()

    def put(self, item):
        with self._cond:
            while len(self._items) >= self._maxsize:
                self._cond.wait()
            self._items.append(item)
            self._cond.notify_all()

    def get(self):
        with self._cond:
            while not self._items:
                self._cond.wait()
            item = self._items.popleft()
            self._cond.notify_all()
            return item
