from __future__ import annotations

from typing import Type

import firefly.domain as ffd
import firefly.infrastructure as ffi
from firefly import Repository
from firefly.domain.repository.repository_factory import E


class DbApiObjectRepositoryFactory(ffd.RepositoryFactory):
    def __init__(self, interface_registry: ffi.DbApiStorageInterfaceRegistry):
        self._interface_registry = interface_registry
        self._mappings = {}
        self._cache = {}
        self._default_interface = None

    def __call__(self, entity: Type[E]) -> Repository:
        if entity not in self._cache:
            interface = None
            if entity in self._mappings:
                interface = self._interface_registry.get(self._mappings[entity])
            elif self._default_interface is not None:
                interface = self._default_interface

            if interface is None:
                raise ffd.ConfigurationError(f'No storage interface defined for entity {entity}')

            class LocalRepository(ffi.DbApiObjectRepository[entity]):
                pass
            LocalRepository.__name__ = f'{entity.__name__}Repository'
            self._cache[entity] = LocalRepository(interface)

        return self._cache[entity]

    def register_storage_interface(self, entity: Type[E], interface: str):
        self._mappings[entity] = interface

    def set_default_storage_interface(self, interface: str):
        self._default_interface = self._interface_registry.get(interface)
