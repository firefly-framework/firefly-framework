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

from typing import Callable, Any

import chalice.app
import cognitojwt

import firefly.domain as ffd
from chalice.app import ForbiddenError, BadRequestError


@ffd.middleware()
class AuthorizeRequest(ffd.Middleware):
    _kernel: ffd.Kernel = None
    _rest_router: ffd.RestRouter = None
    _user_pool_id: str = None
    _region: str = None
    _ff_environment: str = None

    def __init__(self):
        if self._user_pool_id not in (None, ''):
            response = self._kernel.cognito_client.list_user_pool_clients(
                UserPoolId=self._user_pool_id
            )
            clients = []
            try:
                for client in response['UserPoolClients']:
                    clients.append(client['ClientId'])
            except KeyError:
                raise ffd.ApiError('Could not initialize clients list from Cognito')
            self._clients = clients

    def __call__(self, event, get_response: Callable) -> Any:
        request = self._kernel.current_request()
        if request is None or not hasattr(event, 'method'):
            return get_response(event)

        headers = request.headers
        token = None
        for k, v in headers.items():
            if k.lower() == 'authorization':
                token = v.split(' ')[-1]
                break

        if self._ff_environment == 'test':
            return self._handle_test_request(token, event, get_response, self._get_endpoint(event.path, event.method))

        try:
            claims = cognitojwt.decode(token, self._region, self._user_pool_id, app_client_id=self._clients)
        except ValueError:
            claims = {'scope': ''}
        self._validate_token_claims(claims, event.method, event.path)

        return get_response(event)

    def _get_endpoint(self, path: str, method: str):
        endpoint, _ = self._rest_router.match(path, method)
        return endpoint

    def _validate_token_claims(self, claims: dict, method: str, path: str):
        endpoint = self._get_endpoint(path, method)
        if endpoint is not None:
            if endpoint.secured is False:
                return
            for scope in claims['scope'].split(' '):
                if endpoint.validate_scope(scope):
                    return
            raise ffd.Forbidden()
        raise RuntimeError('Could not match route. This should never happen.')

    def _handle_test_request(self, token: str, event, get_response: Callable, endpoint):
        try:
            print(endpoint)
            if token.lower() == 'allow' or endpoint.secured is False:
                return get_response(event)
        except AttributeError:
            if endpoint.secured is False:
                return get_response(event)

        raise ffd.Forbidden()
