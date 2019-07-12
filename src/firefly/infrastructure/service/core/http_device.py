from __future__ import annotations

import inspect
from dataclasses import asdict

import aiohttp_cors
import firefly.domain as ffd
from aiohttp import web


class HttpDevice(ffd.Device, ffd.LoggerAware):
    _context_map: ffd.ContextMap = None

    def __init__(self, port: int = 8080):
        super().__init__()

        self.port = port
        self._app = web.Application()
        self._cors = aiohttp_cors.setup(self._app)
        self._routes = []

    def run(self):
        for port in self._ports:
            if port.target is None:
                continue

            async def handle_request(request: web.Request, p=port):
                return await self._handle_request(request, p)

            app_route = getattr(web, port.endpoint.method.lower())(
               port.endpoint.path, handle_request
            )
            self.info('Registering endpoint: %s %s', port.endpoint.method, port.endpoint.path)
            self._routes.append(app_route)
            if isinstance(port.cors, dict):
                self._cors.add(app_route, port.cors)

        self._app.add_routes(self._routes)
        web.run_app(self._app, port=self.port)

    async def _handle_request(self, request: web.Request, port: ffd.HttpPort):
        self.info('Received request on port %s', port)
        response = port.handle(body=await request.text(), headers=dict(request.headers))

        print(response)
        return web.Response(
            headers=response.http_headers,
            body=response.body
        )

    def register_port(self, command: ffd.RegisterHttpPort):
        target = command.target
        if target is not None and issubclass(target, ffd.Service):
            target = target.get_message()
        port = ffd.HttpPort(target, asdict(command), command.endpoint, command.cors)
        port._system_bus = self._system_bus
        self._ports.append(port)

    def _build_ports(self, args: dict, parent: ffd.HttpPort = None):
        if 'port_type' in args:
            del args['port_type']
        if '__class__' in args:
            del args['__class__']

        port = ffd.HttpPort(**args)
        if parent is not None:
            port.extend(parent)

        if inspect.isclass(port.target):
            for k, v in port.target.__dict__.items():
                if hasattr(v, '__ff_port'):
                    for kwargs in getattr(v, '__ff_port'):
                        kwargs['target'] = v
                        self._build_ports(kwargs, port)

        if port.path is not None:
            self._ports.append(port)
