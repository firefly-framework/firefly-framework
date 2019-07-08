from abc import ABC

import firefly.domain as ffd


class CrudOperation(ABC):
    MAPPINGS = {
        'create': 'Created',
        'update': 'Updated',
        'delete': 'Deleted',
        'get': 'Fetched',
    }

    def _build_event(self, type_: type, operation: str):
        class CrudEvent(ffd.Event):
            pass
        CrudEvent.__name__ = '{}{}'.format(type_.__name__, self.MAPPINGS[operation])
        event = CrudEvent()
        event.context = type_.__module__.split('.')[0]

        return event
