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

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.pool import NullPool
import firefly.domain as ffd


class EngineFactory:
    _serializer: ffd.Serializer = None
    _db_name: str = None
    _db_user: str = None
    _db_password: str = None
    _db_host: str = None
    _db_type: str = None
    _db_port: str = None

    def __call__(self, echo: bool = False, **kwargs):
        if self._db_type is None:
            self._db_type = 'sqlite'

        if 'sqlite' == self._db_type and '' == self._db_host:
            import sqlite3

            @event.listens_for(Engine, "connect")
            def set_sqlite_pragma(connection, record):
                cursor = connection.cursor()
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.close()

            return create_engine(
                'sqlite:///:memory:',
                creator=lambda: sqlite3.connect('file::memory:?cache=shared', uri=True),
                echo=echo,
                poolclass=NullPool
            )

        return create_engine(
            self.get_connection_string(),
            echo=echo,
            poolclass=NullPool,
            json_serializer=self._serializer.serialize,
            json_deserializer=self._serializer.deserialize
        )

    def get_connection_string(self):
        if self._db_type == 'sqlite':
            return f"sqlite:///{self._db_host}"

        return f"{self._db_type}://{self._db_user}:{self._db_password}@{self._db_host}:{self._db_port}/{self._db_name}"
