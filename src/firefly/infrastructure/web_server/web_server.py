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

import asyncio
import logging
import sys
from _signal import SIGABRT, SIGILL, SIGINT, SIGSEGV, SIGTERM
from signal import signal
from typing import List, Callable

import firefly.domain as ffd

import websockets
from aiohttp import web


class WebServer(ffd.SystemBusAware):
    _serializer: ffd.Serializer = None

    def __init__(self, host: str = '0.0.0.0', port: int = 9000,
                 websocket_host: str = '0.0.0.0', websocket_port: int = 9001):
        self.routes = []
        self.extensions = []
        self.host = host
        self.port = port
        self.websocket_host = websocket_host
        self.websocket_port = websocket_port
        self.app = web.Application()
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def add_extension(self, extension: Callable):
        self.extensions.append(extension)

    def run(self):
        self.initialize()

        self.loop.run_until_complete(
            websockets.serve(self._handle_websocket, host=self.websocket_host, port=self.websocket_port)
        )

        print("Server is running", flush=True)
        web.run_app(self.app, host=self.host, port=self.port)

        self._shut_down()

    def initialize(self):
        self._init_logger()

        for extension in self.extensions:
            extension(self)

        self.app.add_routes(self.routes)

        for sig in (SIGABRT, SIGILL, SIGINT, SIGSEGV, SIGTERM):
            signal(sig, self._shut_down)

    def add_endpoint(self, method: str, route: str):
        self.routes.append(getattr(web, method.lower())(route, self._handle_request))

    async def _handle_request(self, request: web.Request):
        message = self._serializer.deserialize(await request.text())
        if isinstance(message, ffd.Event):
            response = self.dispatch(message)
        elif isinstance(message, ffd.Command):
            response = self.invoke(message)
        else:
            response = self.query(message)

        return web.Response(body=self._serializer.serialize(response))

    async def _handle_websocket(self, websocket, path):
        consumer_task = asyncio.ensure_future(self._consumer(websocket, path))
        producer_task = asyncio.ensure_future(self._producer(websocket, path))
        done, pending = await asyncio.wait([consumer_task, producer_task], return_when=asyncio.FIRST_COMPLETED)
        for task in pending:
            task.cancel()

    async def _consumer(self, websocket, path):
        pass

    async def _producer(self, websocket, path):
        pass

    @staticmethod
    def _init_logger():
        root = logging.getLogger()
        root.setLevel(logging.DEBUG)

        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        root.addFilter(ch)

    def _shut_down(self):
        print("Shutting down")
        self.loop.stop()
        self.loop.close()
