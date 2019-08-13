from __future__ import annotations

from abc import ABC
from typing import Union

import firefly.domain as ffd

from .message_bus import MessageBus


class CommandBus(MessageBus):
    _message_factory: ffd.MessageFactory = None

    def invoke(self, command: Union[ffd.Command, str], data: dict = None):
        if isinstance(command, str) and data is not None:
            command = self._message_factory.command(command, data)
        return self.dispatch(command)


class CommandBusAware(ABC):
    _command_bus: CommandBus = None

    def invoke(self, command: Union[ffd.Command, str], data: dict = None):
        return self._command_bus.invoke(command, data)
