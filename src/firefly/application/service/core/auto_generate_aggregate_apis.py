from __future__ import annotations

import inspect
from typing import Type

import firefly.domain as ffd
import firefly_di as di
import inflection
from firefly.domain.entity.entity import Entity
from firefly.domain.service.core.application_service import ApplicationService
from firefly.domain.service.core.invoke_command import InvokeCommand
from firefly.domain.service.logging.logger import LoggerAware


class AutoGenerateAggregateApis(ApplicationService, LoggerAware):
    _context_map: ffd.ContextMap = None
    _system_bus: ffd.SystemBus = None
    _container: di.Container = None
    _command_resolving_middleware: ffd.CommandResolvingMiddleware = None
    _event_resolving_middleware: ffd.EventResolvingMiddleware = None
    _query_resolving_middleware: ffd.QueryResolvingMiddleware = None

    def __call__(self, context: str, **kwargs):
        ctx = self._context_map.get_context(context)
        if ctx is None:
            return

        for entity in ctx.entities:
            self._process_entity(ctx, entity)

    def _process_entity(self, context: ffd.Context, entity: type):
        if not issubclass(entity, ffd.AggregateRoot) or entity == ffd.AggregateRoot:
            return

        self._create_crud_command_handlers(entity, context)
        self._create_query_handler(entity, context)
        self._register_entity_level_event_listeners(entity, context)
        for k in dir(entity):
            if k.startswith('_'):
                continue

            v = getattr(entity, k)
            if inspect.isfunction(v):
                self._create_invoke_command_handler(entity, context, k)

    def _create_invoke_command_handler(self, entity: Type[Entity], context: ffd.Context, method_name: str):
        command_name = inflection.camelize(method_name)

        class Invoke(InvokeCommand[entity]):
            pass

        Invoke.__name__ = f'Invoke{command_name}'
        fqn = f'{context.name}.{command_name}'

        self._command_resolving_middleware.add_command_handler(self._container.build(Invoke, method=method_name), fqn)
        context.command_handlers[Invoke] = fqn

    def _create_query_handler(self, entity: Type[Entity], context: ffd.Context):
        query_name = inflection.pluralize(entity.__name__)

        class Query(ffd.QueryService[entity]):
            pass

        Query.__name__ = query_name
        fqn = f'{context.name}.{query_name}'

        self._query_resolving_middleware.add_query_handler(self._container.build(Query), fqn)
        context.query_handlers[Query] = fqn

    def _create_crud_command_handlers(self, entity: Type[Entity], context: ffd.Context):
        for action in ('Create', 'Delete', 'Update'):
            self._create_crud_command_handler(context, entity, action)

    def _create_crud_command_handler(self, context: ffd.Context, entity, name_prefix):
        name = f'{name_prefix}Entity'
        base = getattr(ffd, name)

        class Action(base[entity]):
            pass

        name = f'{name_prefix}{entity.__name__}'
        fqn = f'{context.name}.{name}'
        Action.__name__ = name
        self._command_resolving_middleware.add_command_handler(self._container.build(Action), fqn)
        context.command_handlers[Action] = fqn

    def _register_entity_level_event_listeners(self, entity: Type[Entity], context: ffd.Context):
        if hasattr(entity, '__ff_listener'):
            configs = getattr(entity, '__ff_listener')
            for config in configs:
                if 'crud' in config:
                    class DoInvokeOn(ffd.InvokeOn):
                        pass

                    action = None
                    if config['crud'] == 'create':
                        action = 'Create'
                    elif config['crud'] == 'delete':
                        action = 'Delete'
                    elif config['crud'] == 'update':
                        action = 'Update'

                    if action is not None:
                        self._event_resolving_middleware.add_event_listener(
                            self._container.build(DoInvokeOn, command_name=f'{context.name}.{action}{entity.__name__}'),
                            config['event']
                        )
                        if DoInvokeOn not in context.event_listeners:
                            context.event_listeners[DoInvokeOn] = []
                        context.event_listeners[DoInvokeOn].append(config['event'])
