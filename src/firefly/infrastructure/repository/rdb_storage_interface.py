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
from typing import Type, get_type_hints, List, Union, Callable, Dict, Tuple

import firefly.domain as ffd
import inflection
# noinspection PyDataclass
from jinjasql import JinjaSql

from .abstract_storage_interface import AbstractStorageInterface
from .rdb_repository import Index, Column


# noinspection PyDataclass
class RdbStorageInterface(AbstractStorageInterface, ABC):
    _serializer: ffd.Serializer = None
    _registry: ffd.Registry = None
    _j: JinjaSql = None
    _cache: dict = {}
    _sql_prefix = 'sql'
    _map_indexes = False
    _map_all = False
    _identifier_quote_char = '"'

    def __init__(self, **kwargs):
        self._tables_checked = []

    def _add(self, entity: Union[ffd.Entity, List[ffd.Entity]]):
        entities = entity
        if not isinstance(entity, list):
            entities = [entity]

        return self._execute(*self._generate_query(
            entity,
            f'{self._sql_prefix}/insert.sql',
            {'data': list(map(self._data_fields, entities))}
        ))

    def _generate_select(self, entity_type: Type[ffd.Entity], criteria: ffd.BinaryOp = None, limit: int = None,
                         offset: int = None, sort: Tuple[Union[str, Tuple[str, bool]]] = None, count: bool = False):
        indexes = [f.name for f in fields(entity_type)
                   if f.metadata.get('index') is True or f.metadata.get('id') is True]
        data = {
                'columns': self._select_list(entity_type),
                'count': count,
            }
        if criteria is not None:
            data['criteria'] = criteria

        if sort is not None:
            sort_fields = []
            for s in sort:
                if str(s[0]) in indexes or self._map_indexes is False:
                    sort_fields.append(s)
            data['sort'] = sort_fields

        if limit is not None:
            data['limit'] = limit

        if offset is not None:
            data['offset'] = offset

        return self._generate_query(entity_type, f'{self._sql_prefix}/select.sql', data)

    def _all(self, entity_type: Type[ffd.Entity], criteria: ffd.BinaryOp = None, limit: int = None, offset: int = None,
             sort: Tuple[Union[str, Tuple[str, bool]]] = None, raw: bool = False, count: bool = False):
        sql, params = self._generate_select(
            entity_type, criteria, limit=limit, offset=offset, sort=sort, count=count
        )
        results = self._execute(sql, params)

        ret = []
        if count:
            return results[0]['c']

        for row in results:
            self.debug('Result row: %s', dict(row))
            ret.append(self._build_entity(entity_type, row, raw=raw))

        return ret

    def _find(self, uuid: str, entity_type: Type[ffd.Entity]):
        results = self._execute(*self._generate_query(
            entity_type,
            f'{self._sql_prefix}/select.sql',
            {
                'columns': self._select_list(entity_type),
                'criteria': ffd.Attr(entity_type.id_name()) == uuid
            }
        ))

        if len(results) == 0:
            return None

        if len(results) > 1:
            raise ffd.MultipleResultsFound()

        return self._build_entity(entity_type, results[0])

    def _remove(self, entity: Union[ffd.Entity, List[ffd.Entity], Callable]):
        criteria = entity
        if isinstance(entity, list):
            criteria = ffd.Attr(entity[0].id_name()).is_in([e.id_value() for e in entity])
        elif not isinstance(entity, ffd.BinaryOp):
            criteria = ffd.Attr(entity.id_name()) == entity.id_value()

        self._execute(*self._generate_query(entity, f'{self._sql_prefix}/delete.sql', {
            'criteria': criteria
        }))

    def _update(self, entity: ffd.Entity):
        criteria = ffd.Attr(entity.id_name()) == entity.id_value()
        try:
            criteria &= ffd.Attr('version') == getattr(entity, '__ff_version')
        except AttributeError:
            pass

        return self._execute(*self._generate_query(
            entity,
            f'{self._sql_prefix}/update.sql',
            {
                'data': self._data_fields(entity),
                'criteria': criteria
            }
        ))

    @abstractmethod
    def _ensure_connected(self):
        pass

    def clear(self, entity: Type[ffd.Entity]):
        self.execute(*self._generate_query(entity, f'{self._sql_prefix}/truncate_table.sql'))

    def destroy(self, entity: Type[ffd.Entity]):
        self.execute(*self._generate_query(entity, f'{self._sql_prefix}/drop_table.sql'))

    @staticmethod
    def _fqtn(entity: Type[ffd.Entity]):
        return inflection.tableize(entity.get_fqn())

    def _check_prerequisites(self, entity: Type[ffd.Entity]):
        self._ensure_connected()

    def get_entity_columns(self, entity: Type[ffd.Entity]):
        ret = []
        annotations_ = get_type_hints(entity)
        for f in fields(entity):
            if f.name.startswith('_'):
                continue

            c = Column(
                name=f.name,
                type=annotations_[f.name],
                length=f.metadata.get('length', None),
                is_id=f.metadata.get('id', False),
                is_indexed=f.metadata.get('index', False)
            )
            if self._map_all is True:
                ret.append(c)
            elif self._map_indexes and f.metadata.get('index', False):
                ret.append(c)
            elif f.metadata.get('id', False):
                ret.append(c)

        if not self._map_all:
            ret.insert(1, Column(name='document', type=dict))
            ret.insert(2, Column(name='__document', type=dict))
            ret.insert(3, Column(name='version', type=int, default=1))

        return ret

    def get_table_columns(self, entity: Type[ffd.Entity]):
        return self._get_table_columns(entity)

    @abstractmethod
    def _get_table_columns(self, entity: Type[ffd.Entity]):
        pass

    def add_column(self, entity: Type[ffd.Entity], column: Column):
        self.execute(
            *self._generate_query(entity, f'{self._sql_prefix}/add_column.sql', {'column': column})
        )

    def drop_column(self, entity: Type[ffd.Entity], column: Column):
        self.execute(
            *self._generate_query(entity, f'{self._sql_prefix}/drop_column.sql', {'column': column})
        )

    def get_entity_indexes(self, entity: Type[ffd.Entity]):
        ret = []
        table = self._fqtn(entity).replace('.', '_')
        for field_ in fields(entity):
            if 'index' in field_.metadata:
                if field_.metadata['index'] is True:
                    ret.append(
                        Index(table=table, columns=[field_.name], unique=field_.metadata.get('unique', False) is True)
                    )
                elif isinstance(field_.metadata['index'], str):
                    name = field_.metadata['index']
                    idx = next(filter(lambda i: i.name == name, ret))
                    if not idx:
                        ret.append(Index(table=table, columns=[field_.name],
                                         unique=field_.metadata.get('unique', False) is True))
                    else:
                        idx.columns.append(field_.name)
                        if field_.metadata.get('unique', False) is True and idx.unique is False:
                            idx.unique = True

        return ret

    def get_table_indexes(self, entity: Type[ffd.Entity]):
        return self._get_table_indexes(entity)

    @abstractmethod
    def _get_table_indexes(self, entity: Type[ffd.Entity]):
        pass

    def create_index(self, entity: Type[ffd.Entity], index: Index):
        self.execute(
            *self._generate_query(entity, f'{self._sql_prefix}/add_index.sql', {'index': index})
        )

    def drop_index(self, entity: Type[ffd.Entity], index: Index):
        self.execute(
            *self._generate_query(entity, f'{self._sql_prefix}/drop_index.sql', {'index': index})
        )

    def _build_entity(self, entity: Type[ffd.Entity], data, raw: bool = False):
        if raw is True:
            if self._map_all is True:
                return data
            else:
                return self._serializer.deserialize(data['document'])

        version = None
        if self._map_all is False:
            version = data['version']
            data = self._serializer.deserialize(data['document'])

        for k, v in self._get_relationships(entity).items():
            if v['this_side'] == 'one':
                data[k] = self._registry(v['target']).find(data[k])
            elif v['this_side'] == 'many':
                data[k] = list(self._registry(v['target']).filter(
                    lambda ee: getattr(ee, v['target'].id_name()).is_in(data[k])
                ))

        ret = entity.from_dict(data)
        if version is not None:
            setattr(ret, '__ff_version', version)
        return ret

    @staticmethod
    def _generate_index(name: str):
        return ''

    def execute(self, sql: str, params: dict = None):
        self._execute(sql, params)

    @abstractmethod
    def _execute(self, sql: str, params: dict = None):
        pass

    def _generate_query(self, entity: Union[ffd.Entity, List[ffd.Entity], Type[ffd.Entity]], template: str, params: dict = None):
        params = params or {}
        if isinstance(entity, list):
            entity = entity[0]
        if not inspect.isclass(entity):
            entity = entity.__class__

        def mapped_fields(e):
            return self.get_entity_columns(e)

        template = self._j.env.select_template([template, '/'.join(['sql', template.split('/')[1]])])
        data = {
            'fqtn': self._fqtn(entity),
            '_q': self._identifier_quote_char,
            'map_indexes': self._map_indexes,
            'map_all': self._map_all,
            'mapped_fields': mapped_fields,
            'indexes': list(map(lambda e: e.name, self.get_entity_indexes(entity))),
            'ids': entity.id_name() if isinstance(entity.id_name(), list) else [entity.id_name()],
            'field_types': {f.name: f.type for f in fields(entity)},
        }
        data.update(params)
        sql, params = self._j.prepare_query(template, data)

        return " ".join(sql.split()), params

    def create_table(self, entity_type: Type[ffd.Entity]):
        self.execute(
            *self._generate_query(
                entity_type,
                f'{self._sql_prefix}/create_table.sql',
                {'entity': entity_type, }
            )
        )

    def create_schema(self, entity_type: Type[ffd.Entity]):
        self.execute(
            *self._generate_query(
                entity_type,
                f'{self._sql_prefix}/create_schema.sql',
                {'context_name': entity_type.get_class_context()}
            )
        )

    def _data_fields(self, entity: ffd.Entity):
        ret = {}
        for f in self.get_entity_columns(entity.__class__):
            if f.name == 'document' and not hasattr(entity, 'document'):
                ret[f.name] = self._serialize_entity(entity)
            elif f.name == 'version':
                try:
                    ret['version'] = getattr(entity, '__ff_version')
                except AttributeError:
                    ret['version'] = 1
            elif inspect.isclass(f.type) and issubclass(f.type, ffd.AggregateRoot):
                ret[f.name] = getattr(entity, f.name).id_value()
            elif ffd.is_type_hint(f.type):
                origin = ffd.get_origin(f.type)
                args = ffd.get_args(f.type)
                if origin is List:
                    if issubclass(args[0], ffd.AggregateRoot):
                        ret[f.name] = self._serializer.serialize(
                            list(map(lambda e: e.id_value(), getattr(entity, f.name)))
                        )
                    else:
                        ret[f.name] = self._serializer.serialize(getattr(entity, f.name))
                elif origin is Dict:
                    if issubclass(args[1], ffd.AggregateRoot):
                        ret[f.name] = {k: v.id_value() for k, v in getattr(entity, f.name).items()}
                    else:
                        ret[f.name] = self._serializer.serialize(getattr(entity, f.name))
            elif f.type is list or f.type is dict:
                if hasattr(entity, f.name):
                    ret[f.name] = self._serializer.serialize(getattr(entity, f.name))
            else:
                ret[f.name] = getattr(entity, f.name)
                if isinstance(ret[f.name], ffd.ValueObject):
                    ret[f.name] = self._serializer.serialize(ret[f.name])
        return ret

    def _select_list(self, entity: Type[ffd.Entity]):
        if self._map_all:
            return list(map(lambda c: c.name, self.get_entity_columns(entity)))
        return ['document', 'version']
