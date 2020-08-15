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
from typing import Callable, Dict, Type, Union, List

import firefly.domain as ffd
from firefly.domain.entity.messaging.event import Event
from firefly.domain.service.logging.logger import LoggerAware
from firefly.domain.service.messaging.middleware import Middleware


class EventResolvingMiddleware(Middleware, LoggerAware):
    _context_map: ffd.ContextMap = None
    _context: str = None
    _env: str = None

    def __init__(self, event_listeners: Dict[Union[Type[Event], str], List[ffd.ApplicationService]] = None):
        self._event_listeners = {}
        self._initialized = False
        if event_listeners is not None:
            for event, listeners in event_listeners.items():
                self._event_listeners[event.get_fqn() if not isinstance(event, str) else event] = listeners

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

        if message.get_context() != 'firefly' and \
                message.get_context() == self._context and \
                not message.headers.get('external', False) and \
                self._env != 'test':
            self._publish_message(message)
            return next_(message)

        args = message.to_dict(recursive=False)
        args['_message'] = message

        if str(message) in self._event_listeners:
            services = self._event_listeners[str(message)]
            for service in services:
                try:
                    parsed_args = ffd.build_argument_list(args, service)
                    self.info('Calling service with arguments: %s', parsed_args)
                    service(**parsed_args)
                except TypeError as e:
                    self.exception(e)
                    raise ffd.FrameworkError(f'Error calling {service.__class__.__name__}:\n\n{str(e)}')

        return next_(message)

    def _publish_message(self, message: ffd.Message):
        self._context_map.get_context(self._context).container.message_transport.dispatch(message)

    def add_event_listener(self, handler: Union[ffd.ApplicationService, Type[ffd.ApplicationService]],
                           event: Union[Type[Event], str]):
        if inspect.isclass(handler):
            handler = self._context_map.get_context(handler.get_class_context()).container.build(handler)
        key = event.get_fqn() if not isinstance(event, str) else event
        if key not in self._event_listeners:
            self._event_listeners[key] = []
        self._event_listeners[key].append(handler)
