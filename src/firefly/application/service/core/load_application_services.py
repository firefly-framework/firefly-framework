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
from typing import List, Type

import firefly.domain as ffd
import inflection


class LoadApplicationServices(ffd.ApplicationService):
    _context_map: ffd.ContextMap = None
    _event_resolver: ffd.EventResolvingMiddleware = None
    _command_resolver: ffd.CommandResolvingMiddleware = None
    _query_resolver: ffd.QueryResolvingMiddleware = None

    def __call__(self, **kwargs):
        for context in self._context_map.contexts:
            for cls in self._load_module(context):
                self._register_service(cls, context)
                self._add_endpoints(cls, context)

        self.dispatch(ffd.ApplicationServicesLoaded())

    def _register_service(self, cls: Type[ffd.ApplicationService], context: ffd.Context):
        if not cls.is_handler():
            return

        if cls.is_event_listener():
            for event in cls.get_events():
                self._event_resolver.add_event_listener(cls, event)
                if cls not in context.event_listeners:
                    context.event_listeners[cls] = []
                context.event_listeners[cls].append(event)

        if cls.is_command_handler():
            if cls.get_command() is None:
                cls.set_command(self._generate_message_name(cls))
            self._command_resolver.add_command_handler(cls, cls.get_command())
            context.command_handlers[cls] = cls.get_command()

        if cls.is_query_handler():
            if cls.get_query() is None:
                cls.set_query(self._generate_message_name(cls))
            self._query_resolver.add_query_handler(cls, cls.get_query())
            context.query_handlers[cls] = cls.get_query()

    def _add_endpoints(self, cls: Type[ffd.ApplicationService], context: ffd.Context):
        if not cls.has_endpoints():
            return

        for endpoint in cls.get_endpoints():
            if endpoint.message is None:
                if cls in context.command_handlers:
                    endpoint.message = context.command_handlers[cls]
                elif cls in context.query_handlers:
                    endpoint.message = context.query_handlers[cls]
                else:
                    if endpoint.method.lower() == 'get':
                        cls.set_query(self._generate_message_name(cls))
                        endpoint.message = cls.get_query()
                    else:
                        cls.set_command(self._generate_message_name(cls))
                        endpoint.message = cls.get_command()
                    self._register_service(cls, context)

            context.endpoints.append(endpoint)

    @staticmethod
    def _load_module(context: ffd.Context) -> List[Type[ffd.ApplicationService]]:
        module_name = context.config.get('application_service_module', '{}.application.service')
        try:
            module = importlib.import_module(module_name.format(context.name))
        except (ModuleNotFoundError, KeyError):
            return []

        ret = []
        for k, v in module.__dict__.items():
            if not inspect.isclass(v):
                continue
            if issubclass(v, ffd.ApplicationService):
                ret.append(v)

        return ret

    @staticmethod
    def _generate_message_name(cls):
        return f'{cls.get_class_context()}.{inflection.camelize(cls.__name__)}'
