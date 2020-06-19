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
import firefly_di as di
from firefly import Repository
from firefly.domain.repository.repository_factory import E


class RdbRepositoryFactory(ffd.RepositoryFactory):
    _context_map: ffd.ContextMap = None
    _container: di.Container = None

    def __init__(self, interface: ffi.RdbStorageInterface):
        self._interface = interface
        self._cache = {}
        self._default_interface = None

    def __call__(self, entity: Type[E]) -> Repository:
        if entity not in self._cache:
            class LocalRepository(ffi.RdbRepository[entity]):
                pass
            LocalRepository.__name__ = f'{entity.__name__}Repository'
            params = self._get_repository_arguments(entity)
            params['interface'] = self._interface
            self._cache[entity] = self._container.build(LocalRepository, **params)

        return self._cache[entity]

    def _get_repository_arguments(self, entity: Type[E]):
        context = self._context_map.get_context(entity.get_class_context())
        if 'aggregates' not in context.config.get('storage', {}):
            return {}
        aggregates = context.config.get('storage').get('aggregates')
        if entity.__name__ in aggregates and isinstance(aggregates.get(entity.__name__), dict):
            return aggregates.get(entity.__name__)
        if entity.get_fqn() in aggregates and isinstance(aggregates.get(entity.get_fqn()), dict):
            return aggregates.get(entity.get_fqn())

        return {}
