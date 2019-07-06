from __future__ import annotations

from abc import ABC
from typing import List, Union, Callable

from .middleware_stack import MiddlewareStack
import firefly.domain as ffd


class MessageBus:
    _middleware = []

    def __init__(self, middleware: List[Union[ffd.Middleware, Callable]]):
        self._middleware = middleware
        self._handle = MiddlewareStack(self._middleware)

    @property
    def middleware(self):
        return self._handle.middleware

    @middleware.setter
    def middleware(self, value):
        self._handle.middleware = value

    def add(self, item: Union[ffd.Middleware, Callable]):
        self._handle.add(item)
        
    def insert(self, index: int, item: Union[ffd.Middleware, Callable]):
        self._handle.insert(index, item)

    def dispatch(self, message: ffd.Message):
        return self._handle(message)


class MessageBusAware(ABC):
    _bus: MessageBus = None

    def dispatch(self, message: ffd.Message):
        return self._bus.dispatch(message)
