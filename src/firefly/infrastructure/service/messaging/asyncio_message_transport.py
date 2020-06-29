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

import asyncio
from typing import Any

import aiohttp
import firefly.domain as ffd
import inflection
from firefly import Query, Command, Event, SystemBus

from ...web_server.web_server import WebServer


# TODO add messages into the event loop in _web_server
class AsyncioMessageTransport(ffd.MessageTransport, ffd.LoggerAware):
    _web_server: WebServer = None
    _system_bus: SystemBus = None
    _serializer: ffd.Serializer = None

    def dispatch(self, event: Event) -> None:
        pass

    def invoke(self, command: Command) -> Any:
        loop = asyncio.get_event_loop()
        context = inflection.dasherize(command.get_context())
        loop.run_until_complete(self._async_post(f'http://localhost:9000/{context}', command))

    def request(self, query: Query) -> Any:
        loop = asyncio.get_event_loop()
        context = inflection.dasherize(query.get_context())
        loop.run_until_complete(self._async_get(f'http://localhost:9000/{context}', query))

    async def _async_post(self, url: str, command: Command):
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=self._serializer.serialize(command)) as resp:
                print(resp.status)
                print(await resp.text())
                exit()

    async def _async_get(self, url: str, query: Query):
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params={'query': self._serializer.serialize(query)}) as resp:
                print(resp.status)
                print(await resp.text())
                exit()
