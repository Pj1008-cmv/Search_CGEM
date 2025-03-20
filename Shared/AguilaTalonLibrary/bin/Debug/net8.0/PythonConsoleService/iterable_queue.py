import collections
import threading
from datetime import timedelta, datetime

class IterableQueue(object):
    def __init__(self, timeoutSec):
        self._timeoutSec = timeoutSec
        self._stop_event = threading.Event()
        self._response_condition = threading.Condition()
        self._responses = collections.deque()
        self._endtime = datetime.utcnow() + timedelta(seconds = timeoutSec)

    def __iter__(self):
      return self
  
    def __next__(self):
        with self._response_condition:
            while datetime.utcnow() < self._endtime and not self._responses and not self._stop_event.is_set():
                self._response_condition.wait(0.1)
            if datetime.utcnow() >= self._endtime:
                raise TimeoutError(f"Operation timed out after {self._timeoutSec} seconds")
            if len(self._responses) > 0:
                return self._responses.popleft()
            else:
                raise StopIteration()

    def add_response(self, response):
        with self._response_condition:
            self._responses.append(response)
            self._response_condition.notify()

    def close(self):
        self._stop_event.set()
        with self._response_condition:
            self._response_condition.notify()