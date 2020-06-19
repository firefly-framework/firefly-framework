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

from abc import ABC, abstractmethod
from dataclasses import fields
from datetime import datetime
from typing import Type

import firefly.domain as ffd
import inflection


class RdbStorageInterface(ffd.LoggerAware, ABC):
    _serializer: ffd.Serializer = None
    _cache: dict = {}

    def __init__(self):
        self._tables_checked = []
        self._cache = {
            'sql': {
                'insert': {},
                'update': {},
            },
            'indexes': {},
            'parts': {
                'columns': {},
                'values': {},
                'update': {},
                'select': {},
            }
        }

    def disconnect(self):
        self._disconnect()

    @abstractmethod
    def _disconnect(self):
        pass

    def add(self, entity: ffd.Entity):
        self._check_prerequisites(entity.__class__)
        self._add(entity)

    @abstractmethod
    def _add(self, entity: ffd.Entity):
        pass

    def all(self, entity_type: Type[ffd.Entity], criteria: ffd.BinaryOp = None, limit: int = None):
        self._check_prerequisites(entity_type)
        return self._all(entity_type, criteria, limit)

    @abstractmethod
    def _all(self, entity_type: Type[ffd.Entity], criteria: ffd.BinaryOp = None, limit: int = None):
        pass

    def find(self, uuid: str, entity_type: Type[ffd.Entity]):
        self._check_prerequisites(entity_type)
        return self._find(uuid, entity_type)

    @abstractmethod
    def _find(self, uuid: str, entity_type: Type[ffd.Entity]):
        pass

    def remove(self, entity: ffd.Entity):
        self._check_prerequisites(entity.__class__)
        self._remove(entity)

    @abstractmethod
    def _remove(self, entity: ffd.Entity):
        pass

    def update(self, entity: ffd.Entity):
        self._check_prerequisites(entity.__class__)
        self._update(entity)

    @abstractmethod
    def _update(self, entity: ffd.Entity):
        pass

    @abstractmethod
    def _ensure_connected(self):
        pass

    @staticmethod
    def _fqtn(entity: Type[ffd.Entity]):
        return inflection.tableize(entity.get_fqn())

    def _check_prerequisites(self, entity: Type[ffd.Entity]):
        self._ensure_connected()

    def get_indexes(self, entity: Type[ffd.Entity]):
        if entity not in self._cache['indexes']:
            self._cache['indexes'][entity] = []
            for field_ in fields(entity):
                if 'index' in field_.metadata and field_.metadata['index'] is True:
                    self._cache['indexes'][entity].append(field_)

        return self._cache['indexes'][entity]

    def _generate_insert(self, entity: ffd.Entity):
        t = entity.__class__
        sql = f"insert into {self._fqtn(t)} ({self._generate_column_list(t)}) values ({self._generate_value_list(t)})"
        return sql, self._generate_parameters(entity)

    def _generate_update(self, entity: ffd.Entity):
        t = entity.__class__
        sql = f"update {self._fqtn(t)} set {self._generate_update_list(t)} where id = :id"
        return sql, self._generate_parameters(entity)

    @abstractmethod
    def _generate_update_list(self, entity: Type[ffd.Entity]):
        pass

    @abstractmethod
    def _generate_column_list(self, entity: Type[ffd.Entity]):
        pass

    @abstractmethod
    def _generate_select_list(self, entity: Type[ffd.Entity]):
        pass

    @abstractmethod
    def _generate_value_list(self, entity: Type[ffd.Entity]):
        pass

    @abstractmethod
    def _generate_parameters(self, entity: ffd.Entity, part: str = None):
        pass

    @abstractmethod
    def _build_entity(self, entity: Type[ffd.Entity], data, raw: bool = False):
        pass

    @staticmethod
    def _generate_where_clause(criteria: ffd.BinaryOp):
        if criteria is None:
            return '', {}
        return criteria.to_sql()

    @staticmethod
    def _generate_index(name: str):
        return ''

    @staticmethod
    def _db_type(field_):
        if field_.type == 'float' or field_.type is float:
            return 'float'
        if field_.type == 'integer' or field_.type is int:
            return 'integer'
        if field_.type == 'datetime' or field_.type is datetime:
            return 'datetime'
        length = field_.metadata['length'] if 'length' in field_.metadata else 256
        return f'varchar({length})'

    @abstractmethod
    def _generate_create_table(self, entity: Type[ffd.Entity]):
        pass

    @staticmethod
    def _datetime_declaration(name: str):
        return f"`{name}` datetime"

    @staticmethod
    def _generate_extra(columns: list, indexes: list):
        return f", {','.join(columns)}"

    def execute_ddl(self, entity: Type[ffd.Entity]):
        self._execute_ddl(entity)

    @abstractmethod
    def _execute_ddl(self, entity: Type[ffd.Entity]):
        pass

    @abstractmethod
    def raw(self, entity: Type[ffd.Entity], criteria: ffd.BinaryOp = None, limit: int = None):
        pass
