from __future__ import annotations

from typing import Callable

import firefly.domain as ffd

from .middleware import Middleware


class ServiceExecutingMiddleware(Middleware):
    _serializer: ffd.Serializer = None

    def __init__(self, service):
        self._service = service

    def __call__(self, message: ffd.Message, next_: Callable) -> ffd.Message:
        try:
            body = self._serializer.deserialize(message.body())
        except ffd.InvalidArgument:
            if isinstance(message.body(), dict):
                body = message.body()
            else:
                body = {'body': message.body()}

        return next_(self._service(_message=message, **body))
