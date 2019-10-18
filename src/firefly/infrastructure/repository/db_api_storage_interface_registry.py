from __future__ import annotations

from typing import Dict

import firefly.infrastructure as ffi


class DbApiStorageInterfaceRegistry:
    def __init__(self):
        self._connections: Dict[str, ffi.DbApiStorageInterface] = {}

    def add(self, name: str, connection: ffi.DbApiStorageInterface):
        self._connections[name] = connection

    def get(self, name: str) -> ffi.DbApiStorageInterface:
        return self._connections.get(name)

    def disconnect_all(self):
        for name, interface in self._connections.items():
            interface.disconnect()
