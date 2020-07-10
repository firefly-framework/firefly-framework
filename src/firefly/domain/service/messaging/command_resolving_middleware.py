#  Copyright (c) 2019 JD Williams
#
#  This file is part of Firefly, a Python SOA framework built by JD Williams. Firefly is free software; you can
#  redistribute it and/or modify it under the terms of the GNU General Public License as published by the
#  Free Software Foundation; either version 3 of the License, or (at your option) any later version.
#
#  Firefly is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the
#  implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
#  Public License for more details. You should have received a copy of the GNU Lesser General Public
#  License along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#  You should have received a copy of the GNU General Public License along with Firefly. If not, see
#  <http://www.gnu.org/licenses/>.

from __future__ import annotations

import inspect
from pprint import pprint
from typing import Callable, Dict, Type, Union

import firefly.domain as ffd
from firefly.domain.entity.messaging.command import Command
from firefly.domain.service.logging.logger import LoggerAware
from firefly.domain.service.messaging.middleware import Middleware


class CommandResolvingMiddleware(Middleware, LoggerAware):
    _context_map: ffd.ContextMap = None
    _context: str = None
    _env: str = None

    def __init__(self, command_handlers: Dict[Type[Command], ffd.ApplicationService] = None):
        self._command_handlers = {}
        self._initialized = False
        if command_handlers is not None:
            for command, handler in command_handlers.items():
                self._command_handlers[command.get_fqn() if not isinstance(command, str) else command] = handler

    def _initialize(self):
        for command, handler in self._command_handlers.items():
            if inspect.isclass(handler):
                self._command_handlers[command] = \
                    self._context_map.get_context(handler.get_class_context()).container.build(handler)
        self._initialized = True

    def __call__(self, message: ffd.Message, next_: Callable) -> ffd.Message:
        if not self._initialized:
            self._initialize()

        if message.get_context() != 'firefly' and self._context_map.get_context(message.get_context()) is None:
            return self._transfer_message(message)

        args = message.to_dict()
        args['_message'] = message

        if str(message) not in self._command_handlers:
            raise ffd.ConfigurationError(f'No command handler registered for {message}')

        service = self._command_handlers[str(message)]

        parsed_args = ffd.build_argument_list(args, service)
        self.info('Calling service with arguments: %s', parsed_args)
        return service(**parsed_args)

    def _transfer_message(self, message: ffd.Message):
        return self._context_map.get_context(self._context).container.message_transport.invoke(message)

    def has_command_handler(self, handler: str):
        return handler in self._command_handlers

    def add_command_handler(self, handler: Union[ffd.ApplicationService, Type[ffd.ApplicationService]],
                            command: Union[Type[Command], str]):
        if inspect.isclass(handler):
            handler = self._context_map.get_context(handler.get_class_context()).container.build(handler)
        if inspect.isclass(command):
            command = command.get_fqn()
        self._command_handlers[command.get_fqn() if not isinstance(command, str) else command] = handler
