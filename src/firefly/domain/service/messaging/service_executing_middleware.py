from __future__ import annotations

from dataclasses import asdict
from typing import Callable

import firefly.domain as ffd

from .middleware import Middleware


class ServiceExecutingMiddleware(Middleware):
    def __init__(self, service):
        self._service = service

    def __call__(self, message: ffd.Message, next_: Callable) -> ffd.Message:
        return next_(self._service(_message=message, **asdict(message)))

    def __repr__(self):
        return f'<ServiceExecutingMiddleware {repr(self._service)}>'
