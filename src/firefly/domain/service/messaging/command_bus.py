from __future__ import annotations

from abc import ABC

import firefly.domain as ffd

from .message_bus import MessageBus


class CommandBus(MessageBus):
    def invoke(self, command: ffd.Command):
        return self.dispatch(command)


class CommandBusAware(ABC):
    _command_bus: CommandBus = None

    def invoke(self, command: ffd.Command):
        return self._command_bus.invoke(command)
