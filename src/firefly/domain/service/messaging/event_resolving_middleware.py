from __future__ import annotations

import inspect
from dataclasses import asdict
from typing import Callable, TypeVar, Dict, Type, Union

import firefly.domain as ffd
import firefly_di as di

from .middleware import Middleware
from ..core.service import Service
from ...entity.messaging.event import Event

E = TypeVar('E', bound=Event)
S = TypeVar('S', bound=Service)


class EventResolvingMiddleware(Middleware):
    _container: di.Container = None

    def __init__(self, event_listeners: Dict[ffd.Service, Union[Type[E], str]] = None):
        self._event_listeners = event_listeners or {}

    def __call__(self, message: ffd.Message, next_: Callable) -> ffd.Message:
        args = asdict(message)
        args['_message'] = message
        for service, event in self._event_listeners.copy().items():
            if message == event:
                service(**ffd.build_argument_list(args, service))
        return next_(message)

    def add_event_listener(self, handler: Union[ffd.Service, Type[S]], event: Union[Type[E], str]):
        if inspect.isclass(handler):
            handler = self._container.build(handler)
        self._event_listeners[handler] = event
