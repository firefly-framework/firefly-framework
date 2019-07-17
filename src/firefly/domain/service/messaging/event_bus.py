from __future__ import annotations

from abc import ABC

import firefly.domain as ffd

from .message_bus import MessageBus


class EventBus(MessageBus):
    def dispatch(self, event: ffd.Event):
        return super().dispatch(event)


class EventBusAware(ABC):
    _event_bus: EventBus = None

    def dispatch(self, event: ffd.Event):
        return self._event_bus.dispatch(event)
