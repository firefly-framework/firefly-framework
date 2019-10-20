#  Copyright (c) 2019 JD Williams
#
#  This file is part of Firefly, a Python SOA framework built by JD Williams. Firefly is free software; you can
#  redistribute it and/or modify it under the terms of the GNU General Public License as published by the
#  Free Software Foundation; either version 3 of the License, or (at your option) any later version.
#
#  Firefly is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the
#  implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
#  Public License for more details. You should have received a copy of the GNU Lesser General Public
#  License along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#  You should have received a copy of the GNU General Public License along with Firefly. If not, see
#  <http://www.gnu.org/licenses/>.

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
