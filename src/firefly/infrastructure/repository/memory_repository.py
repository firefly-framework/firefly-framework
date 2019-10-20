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

from typing import List

import firefly.domain as ffd
from firefly.domain.repository.repository import T


class MemoryRepository(ffd.Repository[T]):
    def __init__(self):
        self.entities = []

    def all(self) -> List[T]:
        return self.entities

    def add(self, entity: T):
        self.entities.append(entity)

    def remove(self, entity: T):
        self.entities.remove(entity)

    def update(self, entity: T):
        self.remove(entity)
        self.add(entity)

    def find(self, uuid) -> T:
        for e in self.entities:
            if e.id_value() == uuid:
                return e

    def find_all_matching(self, criteria: ffd.BinaryOp) -> List[T]:
        ret = []
        for entity in self.entities:
            if criteria.matches(entity):
                ret.append(entity)

        return ret

    def find_one_matching(self, criteria: ffd.BinaryOp) -> T:
        for entity in self.entities:
            if criteria.matches(entity):
                return entity

        return None
