from __future__ import annotations

from dataclasses import asdict
from typing import Callable, TypeVar, Dict, Type

import firefly.domain as ffd

from .middleware import Middleware
from ...entity.messaging.query import Query

Q = TypeVar('Q', bound=Query)


class QueryResolvingMiddleware(Middleware):
    def __init__(self, query_handlers: Dict[ffd.Service, Type[Q]] = None):
        self._query_handlers = query_handlers or {}

    def __call__(self, message: ffd.Message, next_: Callable) -> ffd.Message:
        args = asdict(message)
        args['_message'] = message
        for service, query in self._query_handlers.items():
            if message == query:
                return service(**ffd.build_argument_list(args, service))
        raise ffd.ConfigurationError(f'No query handler registered for {message}')

    def add_query_handler(self, handler: ffd.Service, command: Type[Q]):
        self._query_handlers[handler] = command
