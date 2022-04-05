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
from dataclasses import fields
from typing import Type, get_type_hints, List, Union, Callable, Dict, Tuple

import inflection
from firefly.domain.service.logging.logger import LoggerAware
from firefly.domain.utils import HasMemoryCache
from sqlalchemy import MetaData, Column, Index
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session


# noinspection PyDataclass
class SqlalchemyStorageInterface(HasMemoryCache, LoggerAware):
    _context_map: ContextMap = None
    _map_entities: MapEntities = None
    _metadata: MetaData = None
    _session: Session = None
    _engine: Engine = None

    def __init__(self):
        if not self._cache_get('initialized'):
            self._initialize()
            self._cache_set('initialized', True)

    def _initialize(self):
        self._map_entities()
        self._metadata.create_all()

    def create_functions(self):
        pass

    def add(self, entity: Union[Entity, List[Entity]]):
        list(map(
            lambda e: self._session.add(e),
            [entity] if not isinstance(entity, list) else entity
        ))

    def all(self, entity_type: Type[Entity], criteria: BinaryOp = None, limit: int = None, offset: int = None,
             sort: Tuple[Union[str, Tuple[str, bool]]] = None, raw: bool = False, count: bool = False):
        return self._session.query(entity_type).all()

    def find(self, uuid: str, entity_type: Type[Entity]):
        return self._session.query(entity_type).get(uuid)

    def _remove(self, entity: Union[Entity, List[Entity], Callable]):
        if isinstance(entity, (Entity, list)):
            list(map(
                lambda e: self._session.delete(e),
                [entity] if not isinstance(entity, list) else entity
            ))

    def _update(self, entity: Entity):
        criteria = Attr(entity.id_name()) == entity.id_value()
        try:
            criteria &= Attr('version') == getattr(entity, '__ff_version')
        except AttributeError:
            pass

        return self._execute(*self._generate_query(
            entity,
            f'{self._sql_prefix}/update.sql',
            {
                'data': self._data_fields(entity, add_new=True),
                'criteria': criteria
            }
        ))

    def clear(self, entity: Type[Entity]):
        self.execute(*self._generate_query(entity, f'{self._sql_prefix}/truncate_table.sql'))

    def destroy(self, entity: Type[Entity]):
        self.execute(*self._generate_query(entity, f'{self._sql_prefix}/drop_table.sql'))

    @staticmethod
    def _fqtn(entity: Type[Entity]):
        return inflection.tableize(entity.get_fqn())

    def _check_prerequisites(self, entity: Type[Entity]):
        self._ensure_connected()

    def get_entity_columns(self, entity: Type[Entity]):
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
                is_indexed=f.metadata.get('index', False),
                is_required=f.metadata.get('required', False)
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

    def get_table_columns(self, entity: Type[Entity]):
        return self._get_table_columns(entity)

    def add_column(self, entity: Type[Entity], column: Column):
        self.execute(
            *self._generate_query(entity, f'{self._sql_prefix}/add_column.sql', {'column': column})
        )

    def drop_column(self, entity: Type[Entity], column: Column):
        self.execute(
            *self._generate_query(entity, f'{self._sql_prefix}/drop_column.sql', {'column': column})
        )

    def get_entity_indexes(self, entity: Type[Entity]):
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

    def get_table_indexes(self, entity: Type[Entity]):
        return self._get_table_indexes(entity)

    def create_index(self, entity: Type[Entity], index: Index):
        self.execute(
            *self._generate_query(entity, f'{self._sql_prefix}/add_index.sql', {'index': index})
        )

    def drop_index(self, entity: Type[Entity], index: Index):
        self.execute(
            *self._generate_query(entity, f'{self._sql_prefix}/drop_index.sql', {'index': index})
        )

    def _register_aggregate_references(self, entity: Entity):
        for k, v in self._get_relationships(entity.__class__).items():
            val = getattr(entity, k)
            if v['this_side'] == 'one':
                self._do_register_entity(val)
                self._register_aggregate_references(val)
            else:
                list(map(self._do_register_entity, val or []))
                list(map(self._register_aggregate_references, val or []))

    def _do_register_entity(self, entity):
        if isinstance(entity, AggregateRoot):
            self._registry(entity.__class__).register_entity(entity)

    def _build_entity(self, entity: Type[Entity], data, raw: bool = False):
        if raw is True:
            if self._map_all is True:
                return data
            else:
                return self._serializer.deserialize(data['document'])

        version = None
        if self._map_all is False:
            version = data['version']
            data = self._serializer.deserialize(data['document'])

        ret = entity.from_dict(data)
        if version is not None:
            setattr(ret, '__ff_version', version)

        self._register_aggregate_references(ret)

        return ret

    def _cache_aggregate(self, type_: type, id_: str, value: AggregateRoot):
        if not isinstance(self._cache, dict):
            self._cache = {}
        if 'aggregates' not in self._cache:
            self._cache['aggregates'] = {}
        if type_ not in self._cache['aggregates']:
            self._cache['aggregates'][type_] = {}
        self._cache['aggregates'][type_][id_] = value

    @staticmethod
    def _generate_index(name: str):
        return ''

    def execute(self, sql: str, params: dict = None):
        self._execute(sql, params)

    def _generate_query(self, entity: Union[Entity, List[Entity], Type[Entity]], template: str, params: dict = None):
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

    def create_table(self, entity_type: Type[Entity]):
        self.execute(
            *self._generate_query(
                entity_type,
                f'{self._sql_prefix}/create_table.sql',
                {'entity': entity_type, }
            )
        )

    def create_schema(self, entity_type: Type[Entity]):
        print('create_schema')

    def _data_fields(self, entity: Entity, add_new: bool = False):
        ret = {}
        for f in self.get_entity_columns(entity.__class__):
            if f.name == 'document' and not hasattr(entity, 'document'):
                ret[f.name] = self._serialize_entity(entity, add_new=add_new)
            elif f.name == 'version':
                try:
                    ret['version'] = getattr(entity, '__ff_version')
                except AttributeError:
                    ret['version'] = 1
            elif inspect.isclass(f.type) and issubclass(f.type, AggregateRoot):
                try:
                    ret[f.name] = getattr(entity, f.name).id_value()
                except AttributeError:
                    if f.is_required:
                        raise RepositoryError(f"{f.name} is a required field, but no value is present.")
                    ret[f.name] = None
            elif is_type_hint(f.type):
                origin = get_origin(f.type)
                args = get_args(f.type)
                if origin is List:
                    if issubclass(args[0], AggregateRoot):
                        ret[f.name] = self._serializer.serialize(
                            list(map(lambda e: e.id_value(), getattr(entity, f.name)))
                        )
                    else:
                        ret[f.name] = self._serializer.serialize(getattr(entity, f.name))
                elif origin is Dict:
                    if issubclass(args[1], AggregateRoot):
                        ret[f.name] = {k: v.id_value() for k, v in getattr(entity, f.name).items()}
                    else:
                        ret[f.name] = self._serializer.serialize(getattr(entity, f.name))
            elif f.type is list or f.type is dict:
                if hasattr(entity, f.name):
                    ret[f.name] = self._serializer.serialize(getattr(entity, f.name))
            else:
                ret[f.name] = getattr(entity, f.name)
                if isinstance(ret[f.name], ValueObject):
                    ret[f.name] = self._serializer.serialize(ret[f.name])
        return ret

    def _select_list(self, entity: Type[Entity]):
        if self._map_all:
            return list(map(lambda c: c.name, self.get_entity_columns(entity)))
        return ['document', 'version']
