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

import json
import os
import functools
import logging
from json.decoder import JSONDecodeError

import firefly.domain as ffd
from chalice import Chalice
from chalice.app import SQSEvent, AuthRequest, AuthResponse, Request
from chalice.test import Client
from firefly.domain.service.core.application import Application
import firefly.domain.error as errors


class FireflyAuthorizer:
    _kernel: ffd.Kernel = None

    def __init__(self, kernel: ffd.Kernel):
        self._kernel = kernel

    def __call__(self, auth_request: AuthRequest):
        auth_function = os.environ.get('AUTH_FUNCTION')
        resp = self._kernel.system_bus.request(auth_function, data={
            'token': auth_request.token,
        })
        if not isinstance(resp, dict) or 'scope' not in resp:
            routes = self._get_allowed_routes('')
        else:
            routes = self._get_allowed_routes(resp['scope'])

        return AuthResponse(routes=routes, principal_id='user')

    def _get_allowed_routes(self, scope: str):
        ret = []
        for route in self._kernel.get_http_endpoints():
            for s in scope.split(' '):
                if route.validate_scope(s) is True:
                    ret.append(route.route)

        return ret


def http_event(kernel, service, **kwargs):
    request: Request = kernel.current_request()
    try:
        body = kernel.serializer.deserialize(request.raw_body)
        body.update(kwargs)
    except (JSONDecodeError, ffd.InvalidArgument):
        body = kwargs

    response = service(**ffd.build_argument_list(body, service))

    if isinstance(response, ffd.ValueObject):
        response = response.to_dict()

    return json.loads(kernel.serializer.serialize(response))


def sqs_event(event: SQSEvent, kernel: ffd.Kernel, **kwargs):
    for e in event:
        try:
            message = kernel.serializer.deserialize(e.body)
        except ValueError:
            message = e.body

        if isinstance(message, dict) and '_type' in message:
            message = getattr(kernel.message_factory, message['_type'])(
                f"{message['_context']}.{message['_name']}", message
            )

        if isinstance(message, ffd.Command):
            try:
                handler = kernel.get_command_handlers()[str(message)]
                handler(**ffd.build_argument_list(message.to_dict(), handler))
            except KeyError as e:
                raise errors.ConfigurationError(f'No command handler registered for message: {message}') from e

        elif isinstance(message, ffd.Event):
            try:
                for service in kernel.get_event_listeners()[str(message)]:
                    service(**ffd.build_argument_list(message.to_dict(), service))
            except KeyError:
                pass  # Treat a missing event listener as a noop.


def lambda_handler(event, context, service, serializer):
    return service(**ffd.build_argument_list(serializer.deserialize(event).to_dict(), service))


def middleware(event, get_response, service):
    return service(event, get_response)


class ChaliceApplication(Application):
    app: Chalice = None
    configuration: ffd.Configuration = None
    _router: ffd.RestRouter = None
    _context: str = None
    _debug: str = None

    def initialize(self, kernel: ffd.Kernel):
        app_name = self._context
        self.app = Chalice(app_name=app_name)
        self.app.debug = self._debug == '1'
        if self.app.debug:
            self.app.log.setLevel(logging.DEBUG)

        authorizer = FireflyAuthorizer(kernel)
        authorizer.__name__ = 'firefly_authorizer'
        self.app.authorizer()(authorizer)

        for service in kernel.get_middleware():
            self.app.register_middleware(service)

        for config in kernel.get_http_endpoints():
            config['service'].__name__ = config['service'].__class__.__name__
            func = functools.update_wrapper(
                functools.partial(http_event, kernel=kernel, service=config['service']), http_event
            )
            func.__name__ = config['service'].__class__.__name__
            self.app.route(
                path=config['route'],
                methods=[str(config['method']).upper()],
                name=config['service'].__class__.__name__,
                cors=True,
                authorizer=authorizer
            )(func)
            self._router.register(config['route'], ffd.HttpEndpoint(route=config['route'], method=config['method']))

        for k, v in self.configuration.contexts.items():
            if k.startswith('firefly') or (v or {}).get('is_extension', False) is True:
                continue
            memory_settings = (self.configuration.contexts.get('firefly', {}) or {}).get('memory_settings')
            if memory_settings is not None:
                for memory in memory_settings:
                    func = functools.update_wrapper(functools.partial(sqs_event, kernel=kernel), sqs_event)
                    func.__name__ = f'sqs_event_{memory}'
                    self.app.on_sqs_message(
                        queue=kernel.resource_name_generator.queue_name(app_name, memory)
                    )(func)
            else:
                func = functools.update_wrapper(functools.partial(sqs_event, kernel=kernel), sqs_event)
                func.__name__ = f'sqs_event'
                self.app.on_sqs_message(queue=kernel.resource_name_generator.queue_name(app_name))(
                    func
                )

        for endpoint in kernel.get_cli_endpoints():
            func_name = endpoint.service.__name__
            func = functools.update_wrapper(
                functools.partial(lambda_handler, service=kernel.build(endpoint.service), serializer=kernel.serializer),
                lambda_handler
            )
            func.__name__ = func_name
            self.app.lambda_function(name=func_name)(func)

        for k, v in list(kernel.get_command_handlers().items()) + list(kernel.get_query_handlers().items()):
            func_name = str(k).split('.').pop()
            func = functools.update_wrapper(
                functools.partial(lambda_handler, service=v, serializer=kernel.serializer), lambda_handler
            )
            func.__name__ = func_name
            self.app.lambda_function(name=func_name)(func)

    def get_test_client(self):
        return Client(self.app)
