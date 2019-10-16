from __future__ import annotations

import inspect
from collections import OrderedDict
from typing import Callable, Dict, Type, Union

import firefly.domain as ffd
import firefly_di as di

from .middleware import Middleware
from ..core.application_service import ApplicationService
from ...entity.messaging.command import Command


class CommandResolvingMiddleware(Middleware):
    _container: di.Container = None

    def __init__(self, command_handlers: Dict[Type[Command], ffd.ApplicationService] = None):
        self._command_handlers = {}
        self._initialized = False
        if command_handlers is not None:
            for command, handler in command_handlers.items():
                self._command_handlers[command.get_fqn() if not isinstance(command, str) else command] = handler

    def _initialize(self):
        for command, handler in self._command_handlers.items():
            if inspect.isclass(handler):
                self._command_handlers[command] = self._container.build(handler)
        self._initialized = True

    def __call__(self, message: ffd.Message, next_: Callable) -> ffd.Message:
        if not self._initialized:
            self._initialize()

        args = message.to_dict()
        args['_message'] = message

        try:
            service = self._command_handlers[str(message)]
            return service(**ffd.build_argument_list(args, service))
        except KeyError:
            raise ffd.ConfigurationError(f'No command handler registered for {message}')

    def add_command_handler(self, handler: Union[ApplicationService, Type[ApplicationService]],
                            command: Union[Type[Command], str]):
        if inspect.isclass(handler):
            handler = self._container.build(handler)
        self._command_handlers[command.get_fqn() if not isinstance(command, str) else command] = handler
