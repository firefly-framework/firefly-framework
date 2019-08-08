from abc import ABC

import firefly.domain as ffd


class CrudOperation(ABC):
    MAPPINGS = {
        'create': 'Created',
        'update': 'Updated',
        'delete': 'Deleted',
        'retrieve': 'Retrieved',
    }

    _message_factory: ffd.MessageFactory = None

    def _build_event(self, message: ffd.Message, type_: type, operation: str, source_context: str):
        event = self._message_factory.convert_type(message, f'{type_.__name__}{self.MAPPINGS[operation]}', ffd.Event)
        event.source_context = source_context

        return event
