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


class SystemBus:
    _kernel: ffd.Kernel = None
    _message_factory: ffd.MessageFactory = None
    _message_transport: ffd.MessageTransport = None

    def dispatch(self, event: Union[ffd.Event, str], data: dict = None):
        if isinstance(event, str):
            event = self._message_factory.event(event, data or {})
        self._message_transport.dispatch(event)

    def invoke(self, command: Union[ffd.Command, str], data: dict = None, async_: bool = False):
        if isinstance(command, str):
            data = data or {}
            data['_async'] = async_
            command = self._message_factory.command(command, data)
        else:
            setattr(command, '_async', async_)

        return self._message_transport.invoke(command)

    def request(self, query: Union[ffd.Query, str], criteria: Union[ffd.BinaryOp, Callable] = None,
                data: dict = None):
        if criteria is not None and not isinstance(criteria, ffd.BinaryOp):
            criteria = criteria(ffd.EntityAttributeSpy())
        if isinstance(query, str):
            query = self._message_factory.query(query, criteria, data or {})

        return self._message_transport.request(query)


class SystemBusAware:
    _system_bus: SystemBus = None

    def dispatch(self, event: Union[ffd.Event, str], data: dict = None):
        return self._system_bus.dispatch(event, data)

    def invoke(self, command: Union[ffd.Command, str], data: dict = None, async_: bool = False):
        return self._system_bus.invoke(command, data, async_=async_)

    def request(self, request: Union[ffd.Query, str], criteria: Union[ffd.SearchCriteria, Callable] = None,
                data: dict = None):
        return self._system_bus.request(request, criteria, data)
