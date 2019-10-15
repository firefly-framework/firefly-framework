from __future__ import annotations

from typing import Optional

import firefly.domain as ffd
import firefly.infrastructure as ffi


class DefaultAgent(ffd.Agent):
    _web_server: ffi.WebServer = None

    def __init__(self):
        self._deployment: Optional[ffd.Deployment] = None

    def handle(self, deployment: ffd.Deployment, **kwargs):
        self._deployment = deployment
        self._web_server.add_extension(self._register_gateways)
        self._web_server.run()

    def _register_gateways(self, web_server: ffi.WebServer):
        for api_gateway in self._deployment.api_gateways:
            for endpoint in api_gateway.endpoints:
                web_server.add_endpoint(endpoint.method, endpoint.route)
