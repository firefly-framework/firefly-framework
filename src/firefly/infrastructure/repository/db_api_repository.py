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

from typing import List, Callable, Optional

import firefly.domain as ffd
import firefly.infrastructure as ffi
import inflection
from firefly.domain.repository.repository import T


class DbApiRepository(ffd.Repository[T]):
    def __init__(self, interface: ffi.DbApiStorageInterface):
        self._entity_type = self._type()
        self._table = inflection.tableize(self._entity_type.__name__)
        self._interface = interface
        self._entities = None
        self._new_entities = []
        self._index = 0

    def append(self, entity: T):
        self._interface.add(entity)
        self._entities = None

    def remove(self, entity: T):
        self._interface.remove(entity)
        self._entities = None

    def find(self, uuid) -> T:
        return self._interface.find(uuid, self._entity_type)

    def find_all_matching(self, criteria: ffd.BinaryOp) -> List[T]:
        return self._interface.all(self._entity_type, criteria=criteria)

    def find_one_matching(self, criteria: ffd.BinaryOp) -> T:
        return self._interface.all(self._entity_type, criteria=criteria, limit=1)

    def filter(self, cb: Callable) -> List[T]:
        pass

    def reduce(self, cb: Callable) -> Optional[T]:
        pass

    def __iter__(self):
        return self

    def __next__(self):
        self._load_all()
        if self._index >= len(self._entities):
            self._index = 0
            self._entities = None
            raise StopIteration()
        self._index += 1
        return self._entities[self._index - 1]

    def __len__(self):
        self._load_all()
        return len(self._entities)

    def __getitem__(self, item):
        self._load_all()
        return self._entities[item]

    def _load_all(self):
        if self._entities is None:
            self._entities = self._interface.all(self._entity_type)
