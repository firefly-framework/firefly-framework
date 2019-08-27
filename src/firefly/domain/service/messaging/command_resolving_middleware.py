from __future__ import annotations

import inspect
from dataclasses import asdict
from typing import Callable, TypeVar, Dict, Type, Union

import firefly.domain as ffd
import firefly_di as di

from .middleware import Middleware
from ...entity.messaging.command import Command
from ..core.service import Service

C = TypeVar('C', bound=Command)
S = TypeVar('S', bound=Service)


class CommandResolvingMiddleware(Middleware):
    _container: di.Container = None

    def __init__(self, command_handlers: Dict[ffd.Service, Type[C]] = None):
        self._command_handlers = command_handlers or {}

    def __call__(self, message: ffd.Message, next_: Callable) -> ffd.Message:
        args = asdict(message)
        args['_message'] = message
        for service, command in self._command_handlers.items():
            if message == command:
                return service(**ffd.build_argument_list(args, service))
        raise ffd.ConfigurationError(f'No command handler registered for {message}')

    def add_command_handler(self, handler: Union[ffd.Service, Type[S]], command: Union[Type[C], str]):
        if inspect.isclass(handler):
            handler = self._container.build(handler)
        self._command_handlers[handler] = command
