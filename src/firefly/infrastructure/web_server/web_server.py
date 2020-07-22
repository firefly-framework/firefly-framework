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
import inspect
import logging
import sys
import uuid
from _signal import SIGABRT, SIGILL, SIGINT, SIGSEGV, SIGTERM
from signal import signal
from typing import Callable, Dict
from urllib.parse import parse_qsl

import aiohttp_cors
import firefly.domain as ffd
import websockets
from aiohttp import web
from firefly import TypeOfMessage
from firefly.domain.entity.messaging.http_response import HttpResponse

STATUS_CODES = {
    'BadRequest': 400,
    'Unauthorized': 401,
    'Forbidden': 403,
    'NotFound': 404,
    'ApiError': 500,
}


class WebServer(ffd.SystemBusAware, ffd.LoggerAware):
    _serializer: ffd.Serializer = None
    _message_factory: ffd.MessageFactory = None
    _rest_router: ffd.RestRouter = None

    def __init__(self, host: str = '0.0.0.0', port: int = 9000,
                 websocket_host: str = '0.0.0.0', websocket_port: int = 9001):
        self.routes = []
        self.extensions = []
        self.queues: Dict[str, asyncio.Queue] = {}
        self.queue_map: Dict[str, str] = {}
        self.cors = None
        self.host = host
        self.port = port
        if host.count(':') > 1:
            parts = host.split(':')
            self.port = parts.pop()
            self.host = ':'.join(parts)
        self.websocket_host = websocket_host
        self.websocket_port = websocket_port
        self.app = None
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def add_extension(self, extension: Callable):
        self.extensions.append(extension)

    def run(self):
        self.initialize()

        self.loop.run_until_complete(
            websockets.serve(self._handle_websocket, host=self.websocket_host, port=self.websocket_port)
        )

        print(f"Server is running on {self.host}:{self.port}", flush=True)
        web.run_app(self.app, host=self.host, port=self.port)

        self._shut_down()

    def initialize(self):
        self.app = web.Application()
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
        if message.get_context() != 'firefly':
            self.debug('Broadcasting message %s', message)
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

            endpoint, params = self._rest_router.match(request.path, request.method)
            if endpoint is not None:
                if endpoint.message is not None:
                    message_name = endpoint.message if isinstance(endpoint.message, str) else endpoint.message.get_fqn()
                else:
                    message_name = endpoint.service
                    if inspect.isclass(message_name):
                        message_name = message_name.get_fqn()
                if request.method.lower() == 'get':
                    params.update(request.query)
                    message = self._message_factory.query(message_name, None, params)
                else:
                    text = await request.text()
                    if text and len(text):
                        params.update(self._serializer.deserialize(text))
                    message = self._message_factory.command(message_name, params)
            else:
                if msg is not None:
                    message_name = msg
                    if inspect.isclass(msg):
                        message_name = message_name.get_fqn()
                    if request.method.lower() == 'get':
                        message = self._message_factory.query(message_name, None, dict(request.query))
                    elif request.method.lower() == 'post':
                        data = await request.text()
                        try:
                            data = dict(self._serializer.deserialize(data))
                        except ffd.InvalidArgument:
                            data = dict(parse_qsl(data))
                        data.update(dict(request.query))
                        message = self._message_factory.command(message_name, data)
                elif request.method.lower() == 'post':
                    message: ffd.Message = self._serializer.deserialize(await request.text())
                else:
                    message: ffd.Message = self._serializer.deserialize(request.query['query'])

                if isinstance(message, dict):
                    endpoint, params = self._rest_router.match(request.path, request.method)
                    if endpoint.message is not None:
                        message_name = endpoint.message if isinstance(endpoint.message, str) else endpoint.message.get_fqn()
                    else:
                        message_name = endpoint.service
                        if inspect.isclass(message_name):
                            message_name = message_name.get_fqn()
                    if request.method.lower() == 'get':
                        message = self._message_factory.query(message_name, None, message)
                    else:
                        message = self._message_factory.command(message_name, message)

            self.debug(f'Decoded message: {message.to_dict()}')

            try:
                message.headers['client_id'] = request.headers['Firefly-Client-ID']
            except KeyError:
                self.info('Request missing header Firefly-ClientID')

            response = None

            await self._marshal_request(message, request, endpoint)

            status_code = None
            try:
                if isinstance(message, ffd.Event):
                    response = self.dispatch(message)
                elif isinstance(message, ffd.Command):
                    response = self.invoke(message)
                elif isinstance(message, ffd.Query):
                    response = self.request(message)
            except ffd.UnauthenticatedError as e:
                print(str(e))
                response = {}
                status_code = 403
            except ffd.UnauthorizedError:
                response = {}
                status_code = 401
            except ffd.ApiError as e:
                response = str(e)
                status_code = STATUS_CODES[e.__class__.__name__]

            self.debug(f'Response: {response}')

            if isinstance(response, HttpResponse):
                body = response.body
                headers = response.headers
            else:
                body = self._serializer.serialize(response)
                headers = {}

            params = {'body': body, 'headers': headers}
            if status_code:
                params['status'] = status_code

            return web.Response(**params)

        return _handle_request

    @staticmethod
    async def _marshal_request(message: ffd.Message, request: web.Request, endpoint: ffd.HttpEndpoint):
        # TODO make a class
        message.headers = {
            'http_request': {
                'headers': dict(request.headers),
                'method': request.method,
                'path': request.path,
                'content_type': request.content_type,
                'content_length': request.content_length,
                'query': dict(request.query),
                'post': dict(await request.post()),
                'url': request._message.url,
            }
        }

        if endpoint is not None:
            message.headers['secured'] = endpoint.secured
            message.headers['scopes'] = endpoint.scopes

    async def _handle_websocket(self, websocket, path):
        id_ = str(uuid.uuid4())
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
