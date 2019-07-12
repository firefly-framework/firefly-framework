from __future__ import annotations

from typing import List

from .middleware import Middleware
import firefly.domain as ffd


class MiddlewareStack:
    def __init__(self, middleware: List[Middleware]):
        self._middleware = middleware

    @property
    def middleware(self):
        return self._middleware

    @middleware.setter
    def middleware(self, value: List[Middleware]):
        self._middleware = value

    def add(self, item: Middleware):
        self._middleware.append(item)

    def insert(self, index: int, item: Middleware):
        self._middleware.insert(index, item)

    def __call__(self, msg: ffd.Message):
        def cb(message, *args, **kwargs):
            return message
        for m in reversed(self._middleware):
            def cb(message, next_=cb, mw=m):
                return mw(message, next_=next_)

        return cb(msg)
