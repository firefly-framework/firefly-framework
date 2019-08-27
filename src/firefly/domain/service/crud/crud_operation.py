from __future__ import annotations

from abc import ABC

import firefly.domain as ffd


class CrudOperation(ABC):
    MAPPINGS = {
        'create': 'Created',
        'update': 'Updated',
        'delete': 'Deleted',
    }

    _message_factory: ffd.MessageFactory = None

    def _build_event(self, type_: type, operation: str, data: dict = None, source_context: str = None):
        event = self._message_factory.event(f'{type_.__name__}{self.MAPPINGS[operation]}', data or {})
        if source_context is not None:
            event.source_context = source_context

        return event
