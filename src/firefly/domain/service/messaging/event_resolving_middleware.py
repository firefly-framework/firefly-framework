from __future__ import annotations

import inspect
from typing import Callable, Dict, Type, Union, List

import firefly.domain as ffd

from .middleware import Middleware
from ..core.application_service import ApplicationService
from ...entity.messaging.event import Event


class EventResolvingMiddleware(Middleware):
    _context_map: ffd.ContextMap = None

    def __init__(self, event_listeners: Dict[Union[Type[Event], str], List[ffd.ApplicationService]] = None):
        self._event_listeners = {}
        self._initialized = False
        if event_listeners is not None:
            for event, listeners in event_listeners.items():
                self._event_listeners[event.get_fqn() if not isinstance(event, str) else event] = listeners

    # This is delayed until after __init__ to avoid circular dependencies when building the event listeners.
    # There may be a better way to do this.
    def _initialize(self):
        for event, listeners in self._event_listeners.items():
            built = []
            for listener in listeners:
                if inspect.isclass(listener):
                    built.append(self._context_map.get_context(listener.get_class_context()).container.build(listener))
                else:
                    built.append(listener)
            self._event_listeners[event] = built
        self._initialized = True

    def __call__(self, message: ffd.Message, next_: Callable) -> ffd.Message:
        if not self._initialized:
            self._initialize()

        args = message.to_dict(recursive=False)
        args['_message'] = message

        try:
            services = self._event_listeners[str(message)]
            for service in services:
                service(**ffd.build_argument_list(args, service))
        except KeyError:
            pass

        return next_(message)

    def add_event_listener(self, handler: Union[ApplicationService, Type[ApplicationService]],
                           event: Union[Type[Event], str]):
        if inspect.isclass(handler):
            handler = self._context_map.get_context(handler.get_class_context()).container.build(handler)
        key = event.get_fqn() if not isinstance(event, str) else event
        if key not in self._event_listeners:
            self._event_listeners[key] = []
        self._event_listeners[key].append(handler)
