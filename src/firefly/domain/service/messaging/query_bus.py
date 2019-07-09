from __future__ import annotations

from abc import ABC

import firefly.domain as ffd

from .message_bus import MessageBus


class QueryBus(MessageBus):
    def query(self, request: ffd.Request):
        return self.dispatch(request)


class QueryBusAware(ABC):
    _query_bus: QueryBus = None

    def query(self, request: ffd.Request):
        return self._query_bus.query(request)
