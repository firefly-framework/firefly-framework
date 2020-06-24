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

import importlib
import inspect
from pprint import pprint
from typing import List, Type

import firefly.domain as ffd
import inflection
import typing


class LoadApplicationLayer(ffd.ApplicationService):
    _context_map: ffd.ContextMap = None
    _event_resolver: ffd.EventResolvingMiddleware = None
    _command_resolver: ffd.CommandResolvingMiddleware = None
    _query_resolver: ffd.QueryResolvingMiddleware = None
    _agent_factory: ffd.AgentFactory = None
    _message_factory: ffd.MessageFactory = None
    _rest_router: ffd.RestRouter = None
    _system_bus: ffd.SystemBus = None
    _deferred: List[tuple] = []

    def __call__(self, **kwargs):
        self._deferred = []
        for context in self._context_map.contexts:
            for cls in self._load_module(context):
                if issubclass(cls, ffd.ApplicationService):
                    self._register_service(cls, context)
                    self._add_endpoints(cls, context)
                elif issubclass(cls, ffd.Middleware):
                    self._add_middleware(cls, context)
            for entity in context.entities:
                if issubclass(entity, ffd.AggregateRoot):
                    self._add_endpoints(entity, context)

        for deferred in self._deferred:
            if deferred[0] == 'event':
                self._system_bus.add_event_listener(deferred[1], **deferred[2])
            elif deferred[0] == 'command':
                self._system_bus.add_command_handler(deferred[1], **deferred[2])
            elif deferred[0] == 'query':
                self._system_bus.add_query_handler(deferred[1], **deferred[2])

        self.dispatch(ffd.ApplicationLayerLoaded())

    def _add_middleware(self, cls: Type[ffd.Middleware], context: ffd.Context):
        if not cls.is_middleware():
            return
        config = cls.get_middleware_config()
        params = {}
        if config['index'] is not None:
            params['index'] = config['index']
        elif config['cb'] is not None:
            params['cb'] = config['cb']
        if config['replace'] is not None:
            params['replace'] = config['replace']

        built = context.container.build(cls)
        if config['buses'] is None or 'event' in config['buses']:
            if self._system_bus.add_event_listener(built, **params) is False:
                self._deferred.append(('event', built, params))
        if config['buses'] is None or 'command' in config['buses']:
            if self._system_bus.add_command_handler(built, **params) is False:
                self._deferred.append(('command', built, params))
        if config['buses'] is None or 'query' in config['buses']:
            if self._system_bus.add_query_handler(built, **params) is False:
                self._deferred.append(('query', built, params))

    def _register_service(self, cls: Type[ffd.ApplicationService], context: ffd.Context):
        if cls.is_agent():
            self._agent_factory.register(cls.get_agent(), context.container.build(cls))

        if not cls.is_handler():
            return

        if cls.is_event_listener() and issubclass(cls, ffd.ApplicationService):
            for event in cls.get_events():
                self._event_resolver.add_event_listener(cls, event)
                if cls not in context.event_listeners:
                    context.event_listeners[cls] = []
                context.event_listeners[cls].append(event)

        if cls.is_command_handler() and issubclass(cls, ffd.ApplicationService):
            if cls.get_command() is None:
                cls.set_command(self._generate_message_name(cls))
            cmd = cls.get_command()
            if isinstance(cmd, str):
                cmd = self._message_factory.command_class(cmd, typing.get_type_hints(cls.__call__))
            self._command_resolver.add_command_handler(cls, cmd)
            context.command_handlers[cls] = cmd

        if cls.is_query_handler() and issubclass(cls, ffd.ApplicationService):
            if cls.get_query() is None:
                cls.set_query(self._generate_message_name(cls))
            query = cls.get_query()
            if isinstance(query, str):
                query = self._message_factory.query_class(query, typing.get_type_hints(cls.__call__))
            self._query_resolver.add_query_handler(cls, query)
            context.query_handlers[cls] = query

    def _add_endpoints(self, cls: Type[ffd.MetaAware], context: ffd.Context):
        if not cls.has_endpoints():
            return

        for endpoint in cls.get_endpoints():
            if endpoint.message is None:
                if cls in context.command_handlers:
                    endpoint.message = context.command_handlers[cls]
                elif cls in context.query_handlers:
                    endpoint.message = context.query_handlers[cls]
                elif isinstance(endpoint, ffd.HttpEndpoint):
                    if endpoint.method.lower() == 'get':
                        cls.set_query(self._generate_message(cls, 'query'))
                        endpoint.message = cls.get_query()
                    else:
                        cls.set_command(self._generate_message(cls, 'command'))
                        endpoint.message = cls.get_command()
                    self._register_service(cls, context)
                elif isinstance(endpoint, ffd.CliEndpoint):
                    cls.set_command(self._generate_message(cls, 'command'))
                    endpoint.message = cls.get_command()
                    self._register_service(cls, context)

            context.endpoints.append(endpoint)
            if isinstance(endpoint, ffd.HttpEndpoint):
                route_prefix = f'/{inflection.dasherize(context.name)}'
                route = endpoint.route
                if not route.startswith('/'):
                    route = f'/{route}'
                if not route.startswith(route_prefix):
                    route = f'{route_prefix}{route}'
                self._rest_router.register(route, endpoint)

    @staticmethod
    def _load_module(context: ffd.Context) -> List[Type[ffd.ApplicationService]]:
        module_name = context.config.get('application_module', '{}.application')
        try:
            module = importlib.import_module(module_name.format(context.name))
        except (ModuleNotFoundError, KeyError):
            return []

        ret = []
        for k, v in module.__dict__.items():
            if not inspect.isclass(v):
                continue
            if issubclass(v, (ffd.ApplicationService, ffd.Middleware)):
                ret.append(v)

        return ret

    @staticmethod
    def _generate_message_name(cls):
        return f'{cls.get_class_context()}.{inflection.camelize(cls.__name__)}'

    def _generate_message(self, cls, type_: str):
        return getattr(self._message_factory, f'{type_}_class')(
            self._generate_message_name(cls),
            fields_=typing.get_type_hints(cls.__call__)
        )
