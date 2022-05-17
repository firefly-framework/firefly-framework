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

from pprint import pprint

from devtools import debug

import firefly.domain as ffd
from alembic import autogenerate
from alembic.operations import Operations
from alembic.operations.ops import DropTableOp, ModifyTableOps
from alembic.runtime.migration import MigrationContext
from sqlalchemy import MetaData
from sqlalchemy.engine import Engine


class MigrateDatabase:
    _get_project_root: ffd.GetProjectRoot = None
    _engine: Engine = None
    _metadata: MetaData = None
    _script = None
    _context: str = None

    def __call__(self, create: bool = False):
        if create is True:
            return self._metadata.create_all(checkfirst=True)

        def include_name(name, type_, parent_names):
            if type_ == "schema":
                return name == self._context
            else:
                return True
        mc = MigrationContext.configure(self._engine.connect(), opts={
            'include_name': include_name,
            'include_schemas': True,
        })
        migration_script = autogenerate.produce_migrations(mc, self._metadata)
        migration_ops = migration_script.upgrade_ops.ops
        ops = Operations(mc)

        for op in migration_ops:
            if op.schema != self._context:
                continue

            if isinstance(op, DropTableOp):
                continue  # Don't let code drop tables!

            if isinstance(op, ModifyTableOps):
                for op2 in op.ops:
                    try:
                        ops.invoke(op2)  # ProgrammingError
                    except Exception:
                        raise
            else:
                try:
                    ops.invoke(op)
                except Exception:
                    raise
