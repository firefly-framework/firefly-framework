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

from typing import Union, Callable

import firefly.domain as ffd

from firefly.domain.service.messaging.command_bus import CommandBusAware
from firefly.domain.service.messaging.event_bus import EventBusAware
from firefly.domain.service.messaging.query_bus import QueryBusAware


class SystemBus(EventBusAware, CommandBusAware, QueryBusAware):
    def add_event_listener(self, listener: ffd.Middleware, index: int = None, cb: Callable = None):
        if cb is not None:
            index = cb('event', self._event_bus.middleware)
        if index is not None:
            self._event_bus.insert(index, listener)
        else:
            self._event_bus.add(listener)

    def add_command_handler(self, handler: ffd.Middleware, index: int = None, cb: Callable = None):
        if cb is not None:
            index = cb('command', self._command_bus.middleware)
        if index is not None:
            self._command_bus.insert(index, handler)
        else:
            self._command_bus.add(handler)

    # deprecated
    def insert_command_handler(self, index: int, handle: ffd.Middleware):
        self._command_bus.insert(index, handle)

    def add_query_handler(self, handler: ffd.Middleware, index: int = None, cb: Callable = None):
        if cb is not None:
            index = cb('query', self._query_bus.middleware)
        if index is not None:
            self._query_bus.insert(index, handler)
        else:
            self._query_bus.add(handler)


class SystemBusAware:
    _system_bus: SystemBus = None

    def dispatch(self, event: Union[ffd.Event, str], data: dict = None):
        return self._system_bus.dispatch(event, data)

    def invoke(self, command: Union[ffd.Command, str], data: dict = None):
        return self._system_bus.invoke(command, data)

    def request(self, request: Union[ffd.Query, str], criteria: ffd.BinaryOp = None, data: dict = None):
        return self._system_bus.request(request, criteria, data)
