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

from typing import Optional

import firefly.domain as ffd
import firefly.infrastructure as ffi


class DefaultAgent(ffd.Agent):
    _web_server: ffi.WebServer = None

    def __init__(self):
        self._deployment: Optional[ffd.Deployment] = None

    def handle(self, deployment: ffd.Deployment, start_server: bool = True, **kwargs):
        self._deployment = deployment
        self._web_server.add_extension(self._register_gateways)
        if start_server:
            self._web_server.run()

    def _register_gateways(self, web_server: ffi.WebServer):
        for api_gateway in self._deployment.api_gateways:
            for endpoint in api_gateway.endpoints:
                web_server.add_endpoint(endpoint.method, endpoint.route, endpoint.message)
