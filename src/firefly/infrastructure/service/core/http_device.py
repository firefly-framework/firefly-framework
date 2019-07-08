from __future__ import annotations

import inspect

import aiohttp_cors
import firefly.domain as ffd
from aiohttp import web


class HttpDevice(ffd.Device):
    _context_map: ffd.ContextMap = None

    def __init__(self, port: int = 8080):
        super().__init__()

        self._port = port
        self._app = web.Application()
        self._cors = aiohttp_cors.setup(self._app)
        self._routes = []

    def run(self):
        for port in self._ports:
            for route in port.get_routes():
                async def handle_request(request: web.Request, r=route):
                    return await self._handle_request(request, r)

                app_route = getattr(web, route['method'].lower())(
                    route['path'], handle_request
                )
                print('{} {}'.format(route['method'], route['path']))
                self._routes.append(app_route)
                if isinstance(port.cors, dict):
                    self._cors.add(app_route, port.cors)

        self._app.add_routes(self._routes)
        web.run_app(self._app, port=self._port)

    async def _handle_request(self, request: web.Request, route: dict):
        port = route['port']
        request = ffd.Request(body=await request.text(), headers=dict(request.headers))
        request.header('origin', 'http')
        request.header('service', port.service)
        response = self.dispatch(request)

        return web.Response(
            headers=response.headers(),
            body=response.body()
        )

    def register_port(self, **kwargs):
        if kwargs['port_type'] != 'http':
            return

        del kwargs['port_type']
        self._build_ports(kwargs)

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
