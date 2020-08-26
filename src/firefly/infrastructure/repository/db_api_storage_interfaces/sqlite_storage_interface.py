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
from typing import Type, Optional

import firefly.domain as ffd
import inflection

from ..rdb_storage_interface import RdbStorageInterface


class SqliteStorageInterface(RdbStorageInterface, ffd.LoggerAware):
    _serializer: ffd.Serializer = None

    def __init__(self, **kwargs):
        super().__init__()
        self._config = kwargs
        self._connection: Optional[sqlite3.Connection] = None

    def _disconnect(self):
        if self._connection is not None:
            self._connection.close()
            self._connection = None
            self._cache = {}
            self._tables_checked = []

    def _add(self, entity: ffd.Entity):
        cursor = self._connection.cursor()
        cursor.execute(*self._generate_insert(entity))
        self._connection.commit()
        cursor.close()

    def _all(self, entity_type: Type[ffd.Entity], criteria: ffd.BinaryOp = None, limit: int = None):
        cursor = self._connection.cursor()
        sql = f"select obj from {self._fqtn(entity_type)}"
        params = {}

        pruned_criteria = None
        if criteria is not None:
            pruned_criteria = criteria.prune([i.name for i in self.get_indexes(entity_type)])
            clause, params = self._generate_where_clause(pruned_criteria)
            if len(clause) > 0:
                sql = f'{sql} where {clause}'
                self.debug('Searching: %s. Params: %s', sql, params)
        cursor.execute(sql, params)

        ret = []
        row = cursor.fetchone()
        while row is not None:
            self.debug('Result row: %s', dict(row))
            data = self._serializer.deserialize(row['obj'])
            e = entity_type.from_dict(data)
            ret.append(e)
            if limit is not None and len(ret) >= limit:
                break
            row = cursor.fetchone()

        if limit == 1 and len(ret) > 0:
            return ret[0]

        if criteria != pruned_criteria:
            ret = list(filter(lambda ee: criteria.matches(ee), ret))

        return ret

    def _find(self, uuid: str, entity_type: Type[ffd.Entity]):
        cursor = self._connection.cursor()
        sql = f"select obj from {self._fqtn(entity_type)} where id = ?"
        cursor.execute(sql, (uuid,))
        row = cursor.fetchone()
        if row is not None:
            return entity_type.from_dict(self._serializer.deserialize(row['obj']))

    def _remove(self, entity: ffd.Entity):
        cursor = self._connection.cursor()
        sql = f"delete from {self._fqtn(entity.__class__)} where id = ?"
        cursor.execute(sql, (entity.id_value(),))
        self._connection.commit()
        self._remove_from_cache(entity)

    def _update(self, entity: ffd.Entity):
        cursor = self._connection.cursor()
        cursor.execute(*self._generate_update(entity))
        self._connection.commit()
        cursor.close()

    def _ensure_connected(self):
        if self._connection is not None:
            return

        try:
            host = self._config['host']
        except KeyError:
            raise ffd.ConfigurationError(f'host is required in sqlite_storage_interface')

        self._connection = sqlite3.connect(host, detect_types=sqlite3.PARSE_DECLTYPES)
        self._connection.row_factory = sqlite3.Row

    def _execute_ddl(self, entity: Type[ffd.Entity]):
        self._ensure_connected()
        cursor = self._connection.cursor()
        self.debug(self._generate_create_table(entity))
        cursor.execute(self._generate_create_table(entity))

    @staticmethod
    def _fqtn(entity: Type[ffd.Entity]):
        return inflection.tableize(entity.get_fqn()).replace('.', '_')

    def _get(self, entity: ffd.Entity):
        if entity.__class__ in self._cache and entity.id_value() in self._cache[entity.__class__]:
            return self._cache[entity.__class__][entity.id_value()]

    def _set(self, entity: ffd.Entity):
        if entity.__class__ not in self._cache:
            self._cache[entity.__class__] = {}
        self._cache[entity.__class__][entity.id_value()] = entity

    def _remove_from_cache(self, entity: ffd.Entity):
        if entity.__class__ in self._cache and entity.id_value() in self._cache[entity.__class__]:
            del self._cache[entity.__class__][entity.id_value()]

    @staticmethod
    def _datetime_declaration(name: str):
        return f"`{name}` timestamp"

    def _generate_update_list(self, entity: Type[ffd.Entity]):
        values = ['obj=:obj']
        for index in self.get_indexes(entity):
            values.append(f'`{index.name}`=:{index.name}')
        return ','.join(values)

    def _build_entity(self, entity: Type[ffd.Entity], data, raw: bool = False):
        return entity.from_dict(self._serializer.deserialize(data[0]['stringValue']))

    def _generate_select_list(self, entity: Type[ffd.Entity]):
        return 'obj'

    def _generate_column_list(self, entity: Type[ffd.Entity]):
        values = ['id', 'obj']
        for index in self.get_indexes(entity):
            values.append(index.name)
        return ','.join(values)

    def _generate_value_list(self, entity: Type[ffd.Entity]):
        placeholders = [':id', ':obj']
        for index in self.get_indexes(entity):
            placeholders.append(f':{index.name}')
        return ','.join(placeholders)

    def _generate_parameters(self, entity: ffd.Entity, part: str = None):
        obj = self._serializer.serialize(entity.to_dict(force_all=True))
        params = {'id': entity.id_value(), 'obj': obj}
        for field_ in self.get_indexes(entity.__class__):
            params[field_.name] = getattr(entity, field_.name)
        return params

    def _generate_create_table(self, entity: Type[ffd.Entity]):
        columns = []
        indexes = []
        for i in self.get_indexes(entity):
            indexes.append(self._generate_index(i.name))
            if i.type == 'float':
                columns.append(f"`{i.name}` float")
            elif i.type == 'int':
                columns.append(f"`{i.name}` integer")
            elif i.type == 'datetime':
                columns.append(self._datetime_declaration(i.name))
            else:
                length = i.metadata['length'] if 'length' in i.metadata else 256
                columns.append(f"`{i.name}` varchar({length})")
        extra = ''
        if len(columns) > 0:
            self._generate_extra(columns, indexes)
            extra = self._generate_extra(columns, indexes)

        sql = f"""
            create table if not exists {self._fqtn(entity)} (
                id varchar(40)
                , obj longtext not null
                {extra}
                , primary key(id)
            )
        """
        return sql

    def raw(self, entity: Type[ffd.Entity], criteria: ffd.BinaryOp = None, limit: int = None):
        pass
