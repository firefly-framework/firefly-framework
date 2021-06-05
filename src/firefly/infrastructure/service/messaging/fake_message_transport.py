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

import hashlib
from typing import Any, Callable

import firefly.domain as ffd
from firefly import Query, Command, Event
from .asyncio_message_transport import AsyncioMessageTransport


class FakeMessageTransport(ffd.MessageTransport, ffd.LoggerAware):
    _serializer: ffd.Serializer = None
    _asyncio_message_transport: AsyncioMessageTransport = None

    def __init__(self):
        self._responses = {}

    def register_handler(self, message: str, handler: Callable):
        self._responses[message] = handler

    def dispatch(self, event: Event) -> None:
        if str(event) not in self._responses:
            return self._asyncio_message_transport.dispatch(event)
        return self._responses[str(event)](event)

    def invoke(self, command: Command) -> Any:
        if str(command) not in self._responses:
            return self._asyncio_message_transport.invoke(command)
        return self._responses[str(command)](command)

    def request(self, query: Query) -> Any:
        if str(query) not in self._responses:
            return self._asyncio_message_transport.request(query)
        return self._responses[str(query)](query)
