from __future__ import annotations

from typing import Callable, TypeVar, Type

import firefly.domain as ffd

from .middleware import Middleware
from ...entity.messaging.message import Message

M = TypeVar('M', bound=Message)


class SubscriptionWrapper(Middleware):
    def __init__(self, middleware: ffd.Middleware, type_: Type[M]):
        self._middleware = middleware
        self._type = type_

    def __call__(self, message: ffd.Message, next_: Callable) -> ffd.Message:
        if isinstance(message, self._type):
            return self._middleware(message, next_)
        else:
            return next_(message)

    def __repr__(self):
        return '<SubscriptionWrapper {}, {}>'.format(repr(self._middleware), repr(self._type))
