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

import functools
import logging

import firefly.domain as ffd
from chalice import Chalice
from chalice.app import SQSEvent
from chalice.test import Client
from firefly.domain.service.core.application import Application
import firefly.domain.error as errors


def http_event(event, service, **kwargs):
    return service(**ffd.build_argument_list(kwargs, service))


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
            except KeyError as e:
                raise errors.ConfigurationError(f'No event listeners registered for message: {message}') from e


def lambda_handler(event, context, service, **kwargs):
    return service(**ffd.build_argument_list(kwargs, service))


class ChaliceApplication(Application):
    app: Chalice = None
    configuration: ffd.Configuration = None
    _context: str = None
    _debug: str = None

    def initialize(self, kernel: ffd.Kernel):
        app_name = self._context
        self.app = Chalice(app_name=app_name)
        self.app.debug = self._debug == '1'
        if self.app.debug:
            self.app.log.setLevel(logging.DEBUG)

        for config in kernel.get_http_endpoints():
            config['service'].__name__ = config['service'].__class__.__name__
            self.app.route(
                path=config['route'],
                methods=[config['method']],
                name=config['service'].__class__.__name__,
                cors=True,
            )(config['service'])

        for k, v in self.configuration.contexts.items():
            if k.startswith('firefly') or v.get('is_extension', False) is True:
                continue
            memory_settings = (self.configuration.contexts.get('firefly', {}) or {}).get('memory_settings')
            if memory_settings is not None:
                for memory in memory_settings:
                    func = functools.update_wrapper(functools.partial(sqs_event, kernel=kernel), sqs_event)
                    func.__name__ = f'sqs_event_{memory}'
                    globals()[f'sqs_{memory}'] = self.app.on_sqs_message(
                        queue=kernel.resource_name_generator.queue_name(app_name, memory)
                    )(func)
            else:
                func = functools.update_wrapper(functools.partial(sqs_event, kernel=kernel), sqs_event)
                func.__name__ = f'sqs_event'
                globals()['sqs'] = self.app.on_sqs_message(queue=kernel.resource_name_generator.queue_name(app_name))(
                    func
                )

        for k, v in kernel.get_command_handlers().items():
            func_name = str(k).split('.').pop()
            func = functools.update_wrapper(functools.partial(lambda_handler, service=v), lambda_handler)
            globals()[func_name] = self.app.lambda_function(name=func_name)(func)

    def get_test_client(self):
        return Client(self.app)
