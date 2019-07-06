from __future__ import annotations

from typing import Callable

import firefly.domain as ffd
from ..logging.logger import LoggerAware
from .middleware import Middleware


class LoggingMiddleware(Middleware, LoggerAware):
    def __init__(self, message: str = None):
        self._message = message or 'Message added to bus: {}'

    def __call__(self, message: ffd.Message, next_: Callable) -> ffd.Message:
        self.info(self._message, message)
        return next_(message)
