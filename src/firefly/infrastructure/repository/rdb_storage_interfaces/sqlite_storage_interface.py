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

import sqlite3
from typing import Type, Optional, Union

import firefly.domain as ffd
import inflection
from firefly.infrastructure.repository.rdb_repository import Column, Index

from .legacy_storage_interface import LegacyStorageInterface


class SqliteStorageInterface(LegacyStorageInterface, ffd.LoggerAware):
    _serializer: ffd.Serializer = None
    _sql_prefix = 'sqlite'
    _map_indexes = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._config = kwargs
        self._connection: Optional[sqlite3.Connection] = None

    def _disconnect(self):
        if self._connection is not None:
            self._connection.close()
            self._connection = None
            self._tables_checked = []

    def _ensure_connected(self):
        if self._connection is not None:
            return

        try:
            host = self._config['host']
        except KeyError:
            raise ffd.ConfigurationError(f'host is required in sqlite_storage_interface')

        self._connection = sqlite3.connect(host, detect_types=sqlite3.PARSE_DECLTYPES)
        self._connection.row_factory = sqlite3.Row

    @staticmethod
    def _fqtn(entity: Type[ffd.Entity]):
        return inflection.tableize(entity.get_fqn()).replace('.', '_')

    def _build_entity(self, entity: Type[ffd.Entity], data, raw: bool = False):
        if raw:
            return self._serializer.deserialize(data['document'])
        ret = entity.from_dict(self._load_relationships(entity, self._serializer.deserialize(data['document'])))
        setattr(ret, '__ff_version', data['version'])
        return ret

    def _get_table_columns(self, entity: Type[ffd.Entity]):
        ret = []
        results = self._execute(*self._generate_query(entity, f'{self._sql_prefix}/get_columns.sql'))

        for row in results:
            d = dict(row)
            ret.append(Column(name=d['name'], type=d['type']))

        return ret

    def _get_table_indexes(self, entity: Type[ffd.Entity]):
        ret = []
        results = self._execute(*self._generate_query(entity, f'{self._sql_prefix}/get_indexes.sql'))

        for row in results:
            d = dict(row)
            if d['sql'] is None:
                continue
            ret.append(Index(name=d['name']))

        return ret

    def _execute(self, sql: str, params: dict = None):
        self._ensure_connected()
        cursor = self._connection.cursor()
        self.info(sql)
        self.info(params)
        cursor.execute(sql, params)
        self._connection.commit()

        if sql.startswith('update ') or sql.startswith('insert '):
            return cursor.rowcount

        return cursor.fetchall()

    def create_schema(self, entity_type: Type[ffd.Entity]):
        return True
