from __future__ import annotations

import inspect
from typing import TypeVar, Type

import firefly.domain as ffd
import firefly_di as di
import inflection

from .invoke_command import InvokeCommand
from ..core.service import Service
from ..logging.logger import LoggerAware
from ...entity.entity import Entity

E = TypeVar('E', bound=Entity)


class AutoGenerateAggregateApis(Service, LoggerAware):
    _context_map: ffd.ContextMap = None
    _system_bus: ffd.SystemBus = None
    _container: di.Container = None
    _command_resolving_middleware: ffd.CommandResolvingMiddleware = None
    _event_resolving_middleware: ffd.EventResolvingMiddleware = None

    def __call__(self, context: str, **kwargs):
        try:
            context = self._context_map.contexts[context]
        except KeyError:
            return

        for entity in context.entities:
            self._process_entity(context, entity)

    def _process_entity(self, context: ffd.Context, entity: type):
        if not issubclass(entity, ffd.AggregateRoot) or entity == ffd.AggregateRoot:
            return

        self._create_crud_command_handlers(entity, context)
        self._register_entity_level_event_listeners(entity, context)
        for k in dir(entity):
            if k.startswith('_'):
                continue

            v = getattr(entity, k)
            if inspect.isfunction(v):
                self._create_invoke_command_handler(entity, context, k)

    def _create_invoke_command_handler(self, entity: Type[E], context: ffd.Context, method_name: str):
        class Invoke(InvokeCommand[entity]):
            pass

        Invoke.__name__ = f'Invoke{inflection.camelize(method_name)}'

        self._command_resolving_middleware.add_command_handler(
            self._container.build(Invoke, method=method_name),
            f'{context.name}.{inflection.camelize(method_name)}'
        )

    def _create_crud_command_handlers(self, entity: Type[E], context: ffd.Context):
        for action in ('Create', 'Delete', 'Update'):
            self._create_crud_command_handler(context, entity, action)

    def _create_crud_command_handler(self, context, entity, name_prefix):
        name = f'{name_prefix}Entity'
        base = getattr(ffd, name)

        class Action(base[entity]):
            pass

        name = f'{name_prefix}{entity.__name__}'
        Action.__name__ = name
        self._command_resolving_middleware.add_command_handler(
            self._container.build(Action),
            f'{context.name}.{name}'
        )

    def _register_entity_level_event_listeners(self, entity: Type[E], context: ffd.Context):
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
