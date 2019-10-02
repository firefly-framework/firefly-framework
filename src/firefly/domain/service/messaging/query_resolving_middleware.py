from __future__ import annotations

import inspect
from dataclasses import asdict
from typing import Callable, Dict, Type, Union

import firefly.domain as ffd
import firefly_di as di

from .middleware import Middleware
from ..core.application_service import ApplicationService
from ...entity.messaging.query import Query


class QueryResolvingMiddleware(Middleware):
    _container: di.Container = None

    def __init__(self, query_handlers: Dict[ffd.ApplicationService, Type[Q]] = None):
        self._query_handlers = query_handlers or {}

    def __call__(self, message: ffd.Message, next_: Callable) -> ffd.Message:
        args = message.to_dict()
        args['_message'] = message
        for service, query_type in self._query_handlers.items():
            if message.is_this(query_type):
                return service(**ffd.build_argument_list(args, service))
        raise ffd.ConfigurationError(f'No query handler registered for {message}')

    def add_query_handler(self, handler: Union[ApplicationService, Type[ApplicationService]], command: Type[Query]):
        if inspect.isclass(handler):
            handler = self._container.build(handler)
        self._query_handlers[handler] = command
