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

import inspect
from abc import ABC, abstractmethod
from dataclasses import fields
from datetime import datetime
from typing import Type, get_type_hints, List, Union

import firefly.domain as ffd
import inflection


# noinspection PyDataclass
from jinjasql import JinjaSql


class RdbStorageInterface(ffd.LoggerAware, ABC):
    _serializer: ffd.Serializer = None
    _j: JinjaSql = None
    _cache: dict = {}

    def __init__(self, **kwargs):
        self._tables_checked = []

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

    def all(self, entity_type: Type[ffd.Entity], criteria: ffd.BinaryOp = None, limit: int = None, offset: int = None):
        self._check_prerequisites(entity_type)
        return self._all(entity_type, criteria, limit, offset)

    @abstractmethod
    def _all(self, entity_type: Type[ffd.Entity], criteria: ffd.BinaryOp = None, limit: int = None, offset: int = None):
        pass

    def find(self, uuid: str, entity_type: Type[ffd.Entity]):
        self._check_prerequisites(entity_type)
        return self._find(uuid, entity_type)

    @abstractmethod
    def _find(self, uuid: str, entity_type: Type[ffd.Entity]):
        pass

    def remove(self, entity: ffd.Entity, force: bool = False):
        self._check_prerequisites(entity.__class__)
        if hasattr(entity, 'deleted_on') and not force:
            entity.deleted_on = datetime.now()
            self._update(entity)
        else:
            self._remove(entity)

    @abstractmethod
    def _remove(self, entity: ffd.Entity):
        pass

    def update(self, entity: ffd.Entity):
        self._check_prerequisites(entity.__class__)
        if hasattr(entity, 'updated_on'):
            entity.updated_on = datetime.now()
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

    def get_indexes(self, entity: Type[ffd.Entity], include_ids: bool = False):
        key = str(entity) + str(include_ids)
        if key not in self._cache['indexes']:
            self._cache['indexes'][key] = []
            for field_ in fields(entity):
                if 'index' in field_.metadata and field_.metadata['index'] is True:
                    self._cache['indexes'][key].append(field_)
                elif 'id' in field_.metadata and include_ids is True:
                    self._cache['indexes'][key].append(field_)

        return self._cache['indexes'][key]

    @abstractmethod
    def _build_entity(self, entity: Type[ffd.Entity], data, raw: bool = False):
        pass

    @staticmethod
    def _generate_index(name: str):
        return ''

    def execute(self, sql: str, params: dict = None):
        self._execute(sql, params)

    @abstractmethod
    def _execute(self, sql: str, params: dict = None):
        pass

    def migrate_table(self, entity: Type[ffd.Entity]):
        return self._migrate_table(entity)

    @abstractmethod
    def _migrate_table(self, entity: Type[ffd.Entity]):
        pass

    def _generate_query(self, entity: Union[ffd.Entity, Type[ffd.Entity]], template: str, params: dict):
        if not inspect.isclass(entity):
            entity = entity.__class__

        template = self._j.env.select_template([template])
        data = {
            'fqtn': self._fqtn(entity),
        }
        data.update(params)
        sql, params = self._j.prepare_query(template, data)

        return " ".join(sql.split()), params

    # def _get_relationships(self, entity: Type[ffd.Entity]):
    #     cache = self._get_cache_entry(entity)
    #     if 'relationships' not in cache:
    #         relationships = {}
    #         annotations_ = get_type_hints(entity)
    #         for k, v in annotations_.items():
    #             if k.startswith('_'):
    #                 continue
    #             if isinstance(v, type) and issubclass(v, ffd.AggregateRoot):
    #                 relationships[k] = {
    #                     'field_name': k,
    #                     'target': v,
    #                     'this_side': 'one',
    #                 }
    #             elif isinstance(v, type(List)) and issubclass(v.__args__[0], ffd.AggregateRoot):
    #                 relationships[k] = {
    #                     'field_name': k,
    #                     'target': v.__args__[0],
    #                     'this_side': 'many',
    #                 }
    #         cache['relationships'] = relationships
    #
    #     return cache['relationships']
    #
    # def _get_relationship(self, entity: Type[ffd.Entity], inverse_entity: Type[ffd.Entity]):
    #     relationships = self._get_relationships(entity)
    #     for k, v in relationships.items():
    #         if v['target'] == inverse_entity:
    #             return v

    # def _serialize_entity(self, entity: ffd.Entity):
    #     relationships = self._get_relationships(entity.__class__)
    #     if len(relationships.keys()) > 0:
    #         obj = entity.to_dict(force_all=True, skip=relationships.keys())
    #         for k, v in relationships.items():
    #             if v['this_side'] == 'one':
    #                 obj[k] = getattr(entity, k).id_value()
    #             elif v['this_side'] == 'many':
    #                 obj[k] = list(map(lambda kk: kk.id_value(), getattr(entity, k)))
    #     else:
    #         obj = entity.to_dict(force_all=True)
    #
    #     return self._serializer.serialize(obj)
