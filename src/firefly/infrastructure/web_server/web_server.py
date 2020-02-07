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
import uuid
from _signal import SIGABRT, SIGILL, SIGINT, SIGSEGV, SIGTERM
from pprint import pprint
from signal import signal
from typing import List, Callable, Dict

import aiohttp_cors
import firefly.domain as ffd

import websockets
from aiohttp import web
from firefly import TypeOfMessage


class WebServer(ffd.SystemBusAware, ffd.LoggerAware):
    _serializer: ffd.Serializer = None
    _message_factory: ffd.MessageFactory = None

    def __init__(self, host: str = '0.0.0.0', port: int = 9000,
                 websocket_host: str = '0.0.0.0', websocket_port: int = 9001):
        self.routes = []
        self.extensions = []
        self.queues: Dict[str, asyncio.Queue] = {}
        self.queue_map: Dict[str, str] = {}
        self.cors = None
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

        self.cors = aiohttp_cors.setup(self.app, defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
                allow_methods="*"
            )
        })

        for route in list(self.app.router.routes()):
            self.cors.add(route)

        for sig in (SIGABRT, SIGILL, SIGINT, SIGSEGV, SIGTERM):
            signal(sig, self._shut_down)

        def event_listener(message: ffd.Message, next_: Callable):
            self._broadcast(message)
            return next_(message)
        self._system_bus.add_event_listener(event_listener)

    def _broadcast(self, message: ffd.Message):
        print('broadcasting!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        m = self._serializer.serialize(message)
        for queue in self.queues.values():
            queue.put_nowait(m)

    def add_endpoint(self, method: str, route: str, message: TypeOfMessage = None):
        print(f'Endpoint: {method} {route} -> {message}')
        self.routes.append(getattr(web, method.lower())(route, self._request_handler_generator(message)))

    def _request_handler_generator(self, msg: TypeOfMessage = None):
        async def _handle_request(request: web.Request):
            self.debug('Got a request -----------------------')
            self.debug(request.headers)
            self.debug(await request.text())
            self.debug('-------------------------------------')

            if msg is not None:
                if request.method.lower() == 'get':
                    message = self._message_factory.request(msg)
                elif request.method.lower() == 'post':
                    message = self._message_factory.command(msg, self._serializer.deserialize(await request.text()))
            elif request.method.lower() == 'post':
                message: ffd.Message = self._serializer.deserialize(await request.text())
            else:
                message: ffd.Message = self._serializer.deserialize(request.query['query'])

            self.debug(f'Decoded message: {message.to_dict()}')

            try:
                message.headers['client_id'] = request.headers['Firefly-Client-ID']
            except KeyError:
                self.info('Request missing header Firefly-ClientID')

            response = None

            if isinstance(message, ffd.Event):
                response = self.dispatch(message)
            elif isinstance(message, ffd.Command):
                response = self.invoke(message)
            elif isinstance(message, ffd.Query):
                response = self.request(message)

            serialized_response = self._serializer.serialize(response)
            self.debug(f'Response: {serialized_response}')

            return web.Response(body=serialized_response)

        return _handle_request

    async def _handle_websocket(self, websocket, path):
        id_ = str(uuid.uuid1())
        consumer_task = asyncio.ensure_future(self._consumer(websocket, path, id_))
        producer_task = asyncio.ensure_future(self._producer(websocket, path, id_))
        done, pending = await asyncio.wait([consumer_task, producer_task], return_when=asyncio.FIRST_COMPLETED)
        for task in pending:
            task.cancel()

    async def _consumer(self, websocket, path, id_):
        async for m in websocket:
            message = self._serializer.deserialize(m)
            if 'id' in message:
                self.debug(f'Mapping {id_} to client id {message["id"]}')
                self.queue_map[message['id']] = id_

    async def _producer(self, websocket, path, id_):
        self.queues[id_] = asyncio.Queue(loop=self.loop)

        while True:
            m = await self.queues[id_].get()
            print(f'Sending {m}')
            await websocket.send(m)

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
