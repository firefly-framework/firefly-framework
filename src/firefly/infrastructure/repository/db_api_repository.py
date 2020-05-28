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
    def __init__(self, interface: ffi.DbApiStorageInterface, table_name: str = None):
        super().__init__()

        self._entity_type = self._type()
        self._table = table_name or inflection.tableize(self._entity_type.__name__)
        self._interface = interface
        self._index = 0

    def append(self, entity: T):
        self._entities.append(entity)

    def remove(self, entity: T):
        self._deletions.append(entity)

    def find(self, uuid) -> T:
        ret = self._interface.find(uuid, self._entity_type)
        if ret:
            self._register_entity(ret)
        return ret

    def filter(self, cb: Callable) -> List[T]:
        entities = self._interface.all(self._entity_type, criteria=self._get_search_criteria(cb))
        for entity in entities:
            self._register_entity(entity)
        return entities

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

    def commit(self):
        for entity in self._deletions:
            self._interface.remove(entity)

        for entity in self._new_entities():
            self._interface.add(entity)

        for entity in self._changed_entities():
            self._interface.update(entity)
