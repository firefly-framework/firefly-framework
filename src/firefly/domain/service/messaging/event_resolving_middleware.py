from __future__ import annotations

import inspect
from typing import Callable, Dict, Type, Union, OrderedDict

import firefly.domain as ffd
import firefly_di as di

from .middleware import Middleware
from ..core.application_service import ApplicationService
from ...entity.messaging.event import Event


class EventResolvingMiddleware(Middleware):
    _container: di.Container = None

    def __init__(self, event_listeners: Dict[ffd.ApplicationService, Union[Type[Event], str]] = None):
        self._event_listeners = event_listeners or OrderedDict()

    def __call__(self, message: ffd.Message, next_: Callable) -> ffd.Message:
        args = message.to_dict(recursive=False)
        args['_message'] = message
        for service, event_type in self._event_listeners.copy().items():
            if message.is_this(event_type):
                service(**ffd.build_argument_list(args, service))
        return next_(message)

    def add_event_listener(self, handler: Union[ApplicationService, Type[ApplicationService]],
                           event: Union[Type[Event], str]):
        if inspect.isclass(handler):
            handler = self._container.build(handler)
        self._event_listeners[handler] = event
