from abc import ABC
from dataclasses import asdict

import firefly.domain as ffd


class CrudOperation(ABC):
    MAPPINGS = {
        'create': 'Created',
        'update': 'Updated',
        'delete': 'Deleted',
        'retrieve': 'Retrieved',
    }

    _message_factory: ffd.MessageFactory = None

    def _build_event(self, type_: type, operation: str, data: dict, source_context: str = None):
        event = self._message_factory.event(f'{type_.__name__}{self.MAPPINGS[operation]}', data)
        if source_context is not None:
            event.source_context = source_context

        return event
