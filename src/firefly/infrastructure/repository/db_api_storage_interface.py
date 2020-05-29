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

from abc import ABC, abstractmethod
from typing import Type

import firefly.domain as ffd
import inflection


class DbApiStorageInterface(ABC):
    def __init__(self):
        self._tables_checked = []

    def disconnect(self):
        self._disconnect()

    @abstractmethod
    def _disconnect(self):
        pass

    def add(self, entity: ffd.Entity):
        self._check_prerequisites(entity.__class__)
        self._add(entity)

    @abstractmethod
    def _add(self, entity: ffd.Entity):
        pass

    def all(self, entity_type: Type[ffd.Entity], criteria: ffd.BinaryOp = None, limit: int = None):
        self._check_prerequisites(entity_type)
        return self._all(entity_type, criteria, limit)

    @abstractmethod
    def _all(self, entity_type: Type[ffd.Entity], criteria: ffd.BinaryOp = None, limit: int = None):
        pass

    def find(self, uuid: str, entity_type: Type[ffd.Entity]):
        self._check_prerequisites(entity_type)
        return self._find(uuid, entity_type)

    @abstractmethod
    def _find(self, uuid: str, entity_type: Type[ffd.Entity]):
        pass

    def remove(self, entity: ffd.Entity):
        self._check_prerequisites(entity.__class__)
        self._remove(entity)

    @abstractmethod
    def _remove(self, entity: ffd.Entity):
        pass

    def update(self, entity: ffd.Entity):
        self._check_prerequisites(entity.__class__)
        self._update(entity)

    @abstractmethod
    def _update(self, entity: ffd.Entity):
        pass

    @abstractmethod
    def _ensure_connected(self):
        pass

    @abstractmethod
    def _ensure_table_created(self, entity: Type[ffd.Entity]):
        pass

    @staticmethod
    def _fqtn(entity: Type[ffd.Entity]):
        return inflection.tableize(entity.get_fqn())

    def _check_prerequisites(self, entity: Type[ffd.Entity]):
        self._ensure_connected()
        if entity not in self._tables_checked:
            self._ensure_table_created(entity)
            self._tables_checked.append(entity)
