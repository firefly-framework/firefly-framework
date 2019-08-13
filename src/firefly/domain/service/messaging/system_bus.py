from __future__ import annotations

from typing import Union

import firefly.domain as ffd

from .command_bus import CommandBusAware
from .event_bus import EventBusAware
from .query_bus import QueryBusAware


class SystemBus(EventBusAware, CommandBusAware, QueryBusAware):
    def add_event_listener(self, listener: ffd.Middleware):
        self._event_bus.add(listener)

    def add_command_handler(self, handler: ffd.Middleware):
        self._command_bus.add(handler)

    def add_query_handler(self, handler: ffd.Middleware):
        self._query_bus.add(handler)


class SystemBusAware:
    _system_bus: SystemBus = None

    def dispatch(self, event: Union[ffd.Event, str], data: dict = None):
        return self._system_bus.dispatch(event, data)

    def invoke(self, command: Union[ffd.Command, str], data: dict = None):
        return self._system_bus.invoke(command, data)

    def query(self, request: Union[ffd.Query, str], data: dict = None):
        return self._system_bus.query(request, data)
