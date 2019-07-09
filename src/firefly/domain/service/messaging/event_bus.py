from __future__ import annotations

from abc import ABC

import firefly.domain as ffd

from .message_bus import MessageBus


class EventBus(MessageBus):
    def dispatch(self, command: ffd.Event):
        return super().dispatch(command)


class EventBusAware(ABC):
    _event_bus: EventBus = None

    def dispatch(self, command: ffd.Event):
        return self._event_bus.dispatch(command)
