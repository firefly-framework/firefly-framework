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
    def __init__(self):
        self._cache = {}
        self._factories = {}
        self._default_factory = {}

    def __call__(self, entity) -> Repository:
        if not issubclass(entity, ffd.AggregateRoot):
            raise ffd.LogicError('Repositories can only be generated for aggregate roots')

        if entity not in self._cache:
            for k, v in self._factories.items():
                if issubclass(entity, k):
                    self._cache[entity] = v(entity)
                    break
                elif issubclass(k, entity):
                    self._cache[entity] = v(k)
                    break

            context = entity.get_class_context()
            if context in self._default_factory and self._default_factory[context] is not None:
                self._cache[entity] = self._default_factory[context](entity)

            if entity not in self._cache:
                raise ffd.FrameworkError(
                    f'No registry found for entity {entity}. Have you configured a persistence mechanism or extension?'
                )

        return self._cache[entity]

    def register_factory(self, type_: Type[AR], factory: ffd.RepositoryFactory):
        self._factories[type_] = factory

    def set_default_factory(self, context: str, factory: ffd.RepositoryFactory):
        self._default_factory[context] = factory

    def clear_cache(self):
        self._cache = {}

    def get_repositories(self):
        ret = []
        for k, v in self._cache.items():
            ret.append(v)
        self.debug(ret)
        return ret
