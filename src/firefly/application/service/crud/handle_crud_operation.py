from __future__ import annotations

import re
from dataclasses import asdict
from typing import Callable

import firefly.domain as ffd
import firefly.application.service.crud as crud
import inflection


@ffd.query_handler()
@ffd.command_handler()
class HandleCrudOperation(ffd.Middleware):
    _registry: ffd.Registry = None
    _message_factory: ffd.MessageFactory = None
    _system_bus: ffd.SystemBus = None
    _context_map: ffd.ContextMap = None

    def __init__(self):
        self._crud_regex = re.compile('^(Create)|(Retrieve)|(Update)|(Delete)')

    def __call__(self, message: ffd.Message, next_: Callable) -> ffd.Message:
        if isinstance(message, (ffd.CrudCommand, ffd.CrudQuery)):
            entity_type = ffd.load_class(message.headers['entity_fqn'])

            class CrudOperation(self._generic_operation(message.headers['operation'])[entity_type]):
                pass
            handle = CrudOperation()
            handle._registry = self._registry
            handle._message_factory = self._message_factory
            handle._system_bus = self._system_bus

            return next_(handle(message=message, **asdict(message)))

        return next_(message)

    @staticmethod
    def _generic_operation(operation: str):
        return getattr(crud, '{}Entity'.format(inflection.camelize(operation, uppercase_first_letter=True)))

    def _is_crud_message(self, message: ffd.Message):
        return bool(re.search(self._crud_regex, message.__class__.__name__))

    def _handler_exists(self, message: ffd.Message):
        pass
