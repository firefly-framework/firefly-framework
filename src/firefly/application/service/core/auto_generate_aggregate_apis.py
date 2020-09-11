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

import inspect
from typing import Type

import firefly as ff
import firefly.infrastructure as ffi
import firefly_di as di
import inflection
from firefly.domain.entity.entity import Entity
from firefly.domain.service.core.application_service import ApplicationService
from firefly.domain.service.core.invoke_command import InvokeCommand
from firefly.domain.service.logging.logger import LoggerAware


class AutoGenerateAggregateApis(ApplicationService, LoggerAware):
    _context_map: ff.ContextMap = None
    _system_bus: ff.SystemBus = None
    _container: di.Container = None
    _command_resolving_middleware: ff.CommandResolvingMiddleware = None
    _event_resolving_middleware: ff.EventResolvingMiddleware = None
    _query_resolving_middleware: ff.QueryResolvingMiddleware = None

    def __call__(self, **kwargs):
        for context in self._context_map.contexts:
            for entity in context.entities:
                self._process_entity(context, entity)
            if 'extends' in context.config:
                base_context = self._context_map.get_context(context.config['extends'])
                for entity in base_context.entities:
                    entity._context = context.name
                    self._process_entity(context, entity)

    def _process_entity(self, context: ff.Context, entity: type):
        if not issubclass(entity, ff.AggregateRoot) or entity == ff.AggregateRoot:
            return

        self._create_crud_command_handlers(entity, context)
        self._create_query_handler(entity, context)
        self._register_entity_level_event_listeners(entity, context)
        for k in dir(entity):
            if k.startswith('_'):
                continue

            v = getattr(entity, k)
            if inspect.isfunction(v):
                fqn = self._create_invoke_command_handler(entity, context, k)
                if ff.has_meta(v) and ff.has_endpoints(v):
                    for endpoint in ff.get_endpoints(v):
                        endpoint.message = fqn
                        context.endpoints.append(endpoint)

    def _create_invoke_command_handler(self, entity: Type[Entity], context: ff.Context, method_name: str):
        command_name = f'{entity.__name__}::{inflection.camelize(method_name)}'

        class Invoke(InvokeCommand[entity]):
            pass

        Invoke.__name__ = f'Invoke{command_name}'
        fqn = f'{context.name}.{command_name}'

        self._command_resolving_middleware.add_command_handler(self._container.build(Invoke, method=method_name), fqn)
        context.command_handlers[Invoke] = fqn

        return fqn

    def _create_query_handler(self, entity: Type[Entity], context: ff.Context):
        query_name = inflection.pluralize(entity.__name__)

        class Query(ff.QueryService[entity]):
            pass

        Query.__name__ = query_name
        fqn = f'{context.name}.{query_name}'

        self._query_resolving_middleware.add_query_handler(self._container.build(Query), fqn)
        context.query_handlers[Query] = fqn

    def _create_crud_command_handlers(self, entity: Type[Entity], context: ff.Context):
        for action in ('Create', 'Delete', 'Update'):
            self._create_crud_command_handler(context, entity, action)

    def _create_crud_command_handler(self, context: ff.Context, entity, name_prefix):
        name = f'{name_prefix}Entity'
        base = getattr(ff, name)

        class Action(base[entity]):
            pass

        name = f'{name_prefix}{entity.__name__}'
        fqn = f'{context.name}.{name}'

        if not self._command_resolving_middleware.has_command_handler(fqn):
            Action.__name__ = name
            self._command_resolving_middleware.add_command_handler(self._container.build(Action), fqn)
            context.command_handlers[Action] = fqn

    def _register_entity_level_event_listeners(self, entity: Type[ff.AggregateRoot], context: ff.Context):
        if entity.get_create_on() is not None:
            self._register_crud_event_listener(
                entity.get_create_on(), f'{entity.get_class_context()}.Create{entity.__name__}', context
            )
        if entity.get_delete_on() is not None:
            self._register_crud_event_listener(
                entity.get_delete_on(), f'{entity.get_class_context()}.Delete{entity.__name__}', context
            )
        if entity.get_update_on() is not None:
            self._register_crud_event_listener(
                entity.get_update_on(), f'{entity.get_class_context()}.Update{entity.__name__}', context
            )

    def _register_crud_event_listener(self, event: ff.TypeOfEvent, command: str, context: ff.Context):
        class DoInvokeOn(ff.InvokeOn):
            pass

        self._event_resolving_middleware.add_event_listener(
            self._container.build(DoInvokeOn, command_name=command), event
        )
        if DoInvokeOn not in context.event_listeners:
            context.event_listeners[DoInvokeOn] = []

        context.event_listeners[DoInvokeOn].append(event)
