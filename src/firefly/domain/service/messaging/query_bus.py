from __future__ import annotations

from abc import ABC
from typing import Union

import firefly.domain as ffd

from .message_bus import MessageBus


class QueryBus(MessageBus):
    _message_factory: ffd.MessageFactory = None

    def query(self, request: Union[ffd.Query, str], data: dict = None):
        if isinstance(request, str) and data is not None:
            request = self._message_factory.query(request, data)
        return self.dispatch(request)


class QueryBusAware(ABC):
    _query_bus: QueryBus = None

    def query(self, request: Union[ffd.Query, str], data: dict = None):
        return self._query_bus.query(request, data)
