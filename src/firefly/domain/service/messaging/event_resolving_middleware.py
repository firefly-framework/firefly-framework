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
