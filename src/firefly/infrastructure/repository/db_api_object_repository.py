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


class DbApiObjectRepository(ffd.Repository[T]):
    def __init__(self, interface: ffi.DbApiStorageInterface):
        self._entity_type = self._type()
        self._table = inflection.tableize(self._entity_type.__name__)
        self._interface = interface

    def add(self, entity: T):
        self._interface.add(entity)

    def remove(self, entity: T):
        self._interface.remove(entity)

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
        pass

    def __next__(self):
        pass
