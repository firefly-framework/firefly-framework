from __future__ import annotations

import inspect
from typing import TypeVar

import firefly.domain as ffd
import inflection

from .invoke_command import InvokeCommand

E = TypeVar('E', bound=ffd.Entity)


@ffd.on(ffd.DomainEntitiesLoaded)
class AutoGenerateAggregateApis(ffd.Service, ffd.LoggerAware):
    _context_map: ffd.ContextMap = None
    _system_bus: ffd.SystemBus = None

    def __call__(self, context: str, **kwargs):
        try:
            context = self._context_map.contexts[context]
        except KeyError:
            return

        for entity in context.entities:
            self._process_entity(context, entity)

    @staticmethod
    def _process_entity(context: ffd.Context, entity: type):
        if not issubclass(entity, ffd.AggregateRoot) or entity == ffd.AggregateRoot:
            return

        for k, v in entity.__dict__.items():
            if k.startswith('_'):
                continue

            if inspect.isfunction(v):
                class Invoke(InvokeCommand[entity]):
                    pass

                setattr(Invoke, '__ff_command_handler', [{'command': f'{context.name}.{inflection.camelize(k)}'}])
                Invoke.__name__ = f'Invoke{inflection.camelize(k)}'
                context.add_service(Invoke, {'method': k})
