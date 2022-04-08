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

from typing import TypeVar, Type

import firefly.domain as ffd

from .repository import Repository
from ..entity.aggregate_root import AggregateRoot
from ..service.logging.logger import LoggerAware

AR = TypeVar('AR', bound=AggregateRoot)


class Registry(LoggerAware):
    _repository_factory: ffd.RepositoryFactory = None

    def __init__(self):
        self._cache = {}

    def __call__(self, entity) -> Repository:
        if not issubclass(entity, ffd.AggregateRoot):
            raise ffd.LogicError('Repositories can only be generated for aggregate roots')

        for k, v in self._cache.items():
            if entity.same_type(k):
                return v

        if entity not in self._cache:
            self._cache[entity] = self._repository_factory(entity)

        return self._cache[entity]

    def clear_cache(self):
        self._cache = {}

    def get_repositories(self):
        ret = []
        for k, v in self._cache.items():
            ret.append(v)
        self.debug(ret)
        return ret
