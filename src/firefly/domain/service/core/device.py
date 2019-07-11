from __future__ import annotations

from abc import ABC, abstractmethod

import firefly.domain as ffd

from ..messaging.system_bus import SystemBusAware


class Device(SystemBusAware, ABC):
    def __init__(self):
        self._ports = []

    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def register_port(self, command: ffd.Command):
        pass
