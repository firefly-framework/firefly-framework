from __future__ import annotations

from abc import ABC
from typing import Union

import firefly.domain as ffd

from .message_bus import MessageBus


class EventBus(MessageBus):
    _message_factory: ffd.MessageFactory = None

    def dispatch(self, event: Union[ffd.Event, str], data: dict = None):
        if isinstance(event, str) and data is not None:
            event = self._message_factory.event(event, data)
        return super().dispatch(event)


class EventBusAware(ABC):
    _event_bus: EventBus = None

    def dispatch(self, event: Union[ffd.Event, str], data: dict = None):
        return self._event_bus.dispatch(event, data)
