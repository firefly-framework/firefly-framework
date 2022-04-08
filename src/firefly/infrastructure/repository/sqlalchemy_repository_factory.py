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
from firefly.domain.repository.repository_factory import E, RepositoryFactory


class SqlalchemyRepositoryFactory(RepositoryFactory):
    _kernel: ffd.Kernel = None

    def __init__(self):
        self._cache = {}
        self._default_interface = None
        self._initialized = False

    def __call__(self, entity: Type[E]) -> ffd.Repository:
        if entity not in self._cache:
            class LocalRepository(ffi.SqlalchemyRepository[entity]):
                pass
            LocalRepository.__name__ = f'{entity.__name__}Repository'
            self._cache[entity] = self._kernel.build(LocalRepository)
            self._cache[entity]._logger = self._kernel.logger

        return self._cache[entity]
