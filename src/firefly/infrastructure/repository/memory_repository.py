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

from functools import reduce
from typing import List, Callable, Optional, Union

import firefly.domain as ffd
from firefly.domain.repository.repository import T


class MemoryRepository(ffd.Repository[T]):
    def __init__(self):
        super().__init__()
        self.entities = []
        self._index = 0

    def append(self, entity: T):
        self.entities.append(entity)

    def remove(self, entity: T):
        self.entities.remove(entity)

    def find(self, exp: Union[str, Callable]) -> Optional[T]:
        if isinstance(exp, str):
            for e in self.entities:
                if e.id_value() == exp:
                    return e
        else:
            criteria = self._get_search_criteria(exp)
            results = list(filter(lambda i: criteria.matches(i), self.entities))
            if len(results) > 1:
                raise ffd.MultipleResultsFound()
            if len(results) == 0:
                raise ffd.NoResultFound()
            return results[0]

    def filter(self, cb: Callable) -> List[T]:
        criteria = self._get_search_criteria(cb)
        return list(filter(lambda i: criteria.matches(i), self.entities))

    def reduce(self, cb: Callable) -> Optional[T]:
        return reduce(cb, self.entities)

    def __iter__(self):
        return self

    def __next__(self):
        if self._index >= len(self.entities):
            self._index = 0
            raise StopIteration()
        self._index += 1
        return self.entities[self._index - 1]

    def __len__(self):
        return len(self.entities)

    def __getitem__(self, item):
        return self.entities[item]

    def commit(self):
        pass
