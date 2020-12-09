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

import firefly.domain as ff
import firefly.infrastructure as ffi


@ff.cli('firefly migrate-repositories')
class MigrateRepositories(ff.ApplicationService):
    _registry: ff.Registry = None
    _context_map: ff.ContextMap = None

    def __call__(self, **kwargs):
        for context in self._context_map.contexts:
            if context.is_extension:
                continue

            for entity in context.entities:
                if not issubclass(entity, ff.AggregateRoot):
                    continue

                try:
                    repository = self._registry(entity)
                except ff.FrameworkError as e:
                    if 'No registry found' not in str(e):
                        raise e
                    else:
                        continue

                if isinstance(repository, ffi.RdbRepository):
                    print(f'Migrating {repository.__class__.__name__}')
                    repository.migrate_schema()
