# -*- coding: utf-8 -*-
import asyncio
import threading
import time
from functools import wraps

from ratelimiter import RateLimiter


class AsyncRateLimiter(RateLimiter):
    def __call__(self, func):
        @wraps(func)
        async def async_inner_wrapper(*args, **kwargs):
            async with self:
                return await func(*args, **kwargs)

        return async_inner_wrapper if asyncio.iscoroutinefunction(func) else super().__call__

    def __enter__(self):
        self._lock.acquire()
        # We want to ensure that no more than max_calls were run in the allowed
        # period. For this, we store the last timestamps of each call and run
        # the rate verification upon each __enter__ call.
        if len(self.calls) >= self.max_calls:
            until = time.time() + self.period - self._timespan
            if self.callback:
                t = threading.Thread(target=self.callback, args=(until,))
                t.daemon = True
                t.start()
            sleeptime = until - time.time()
            if sleeptime > 0:
                time.sleep(sleeptime)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Store the last operation timestamp.
        self.calls.append(time.time())

        # Pop the timestamp list front (ie: the older calls) until the sum goes
        # back below the period. This is our 'sliding period' window.
        while self._timespan >= self.period:
            self.calls.popleft()

        self._lock.release()

    async def __aenter__(self):
        await self._alock.acquire()

        # We want to ensure that no more than max_calls were run in the allowed
        # period. For this, we store the last timestamps of each call and run
        # the rate verification upon each __enter__ call.
        if len(self.calls) >= self.max_calls:
            until = time.time() + self.period - self._timespan
            if self.callback:
                asyncio.ensure_future(self.callback(until))
            sleeptime = until - time.time()
            if sleeptime > 0:
                await asyncio.sleep(sleeptime)
        return self

    async def __aexit__(self, *args):
        self.calls.append(time.time())
        # Pop the timestamp list front (ie: the older calls) until the sum goes
        # back below the period. This is our 'sliding period' window.
        while self._timespan >= self.period:
            self.calls.popleft()

        self._alock.release()
