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
from datetime import datetime, date
from pprint import pprint
from typing import Type, get_type_hints, List, Union, Callable, Dict, Tuple

import firefly.domain as ffd
import inflection
from sqlalchemy import MetaData, Float, Integer, DateTime, Text, String, Boolean, Date, ForeignKey, Column, Table, \
    Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.engine import Engine
from sqlalchemy.exc import InvalidRequestError, ProgrammingError
from sqlalchemy.orm import Session, mapper, relationship
from sqlalchemy.sql.ddl import CreateSchema

TYPE_MAPPINGS = {
    float: lambda: Float(48),
    int: lambda: Integer,
    datetime: lambda: DateTime,
    date: lambda: Date,
    bool: lambda: Boolean,
}


# noinspection PyDataclass
class SqlalchemyStorageInterface(ffd.HasMemoryCache, ffd.LoggerAware):
    _context_map: ffd.ContextMap = None
    _metadata: MetaData = None
    _session: Session = None
    _engine: Engine = None
    _stack: list = None

    def __init__(self):
        if not self._cache_get('initialized'):
            self._initialize()
            self._cache_set('initialized', True)

    def _initialize(self):
        self._stack = []
        for context in self._context_map.contexts:
            if context.name == 'firefly':
                continue
            for entity in context.entities:
                self._map_entity(entity)
        self._metadata.create_all()

    def _map_entity(self, entity: Type[ffd.Entity]):
        self.debug(f'_map_entity: {entity}')
        if entity in self._stack:
            self.debug(f'Entity {entity} is already mapped or being mapped. Bailing out.')
            return
        self._stack.append(entity)

        schema, table_name = self._fqtn(entity).split('.')
        try:
            self._engine.execute(CreateSchema(schema))
        except ProgrammingError as e:
            if 'already exists' not in str(e):
                raise e
        args = [table_name, self._metadata]
        kwargs = {
            'schema': schema,
        }
        types = get_type_hints(entity)
        indexes = {}
        relationships = self._get_relationships(entity)
        join_table = None

        for field in fields(entity):
            if field.name.startswith('_'):
                self.debug(f'Skipping private property {field.name}')
                continue

            t = types[field.name]
            column_args = [field.name]
            column_kwargs = {}

            if inspect.isclass(t) and issubclass(t, ffd.Entity):
                self._map_entity(t)
                column_args[0] = column_args[0] + '_id'
                column_args.append(UUID)

            elif ffd.is_type_hint(t) and ffd.get_origin(t) is List:
                self._map_entity(ffd.get_args(t)[0])
                if relationships[field.name]['target_property'] is not None and \
                        relationships[field.name]['other_side'] == 'many':
                    names = [table_name, self._fqtn(relationships[field.name]['target']).split('.')[-1]]
                    names.sort()
                    join_table = Table(
                        f'{names[0]}_{names[1]}',
                        self._metadata,
                        Column(inflection.underscore(entity.__name__)),
                        Column(inflection.underscore(relationships[field.name]['target'].__name__))
                    )
                self.debug(f'property {field.name} is a list... not adding any columns')
                continue

            elif t is str:
                self.debug(f'{field.name} is a string')
                length = field.metadata.get('length')
                if length is None:
                    self.debug('No length... mapping as text field')
                    column_args.append(Text)
                else:
                    self.debug('Has a length... mapping as varchar')
                    column_args.append(String(length=length))

            else:
                self.debug(f'Default type mapping: {TYPE_MAPPINGS[t]()}')
                column_args.append(TYPE_MAPPINGS[t]())

            if field.metadata.get('id') is True:
                self.debug(f'{field.name} is an id')
                if field.metadata.get('is_uuid') is True:
                    self.debug(f'column is a uuid, changing type to UUID')
                    column_args[1] = UUID
                column_kwargs['primary_key'] = True

            if field.metadata.get('required') is True:
                self.debug(f'{field.name} is required. Setting nullable to false')
                column_kwargs['nullable'] = False

            if inspect.isclass(t) and issubclass(t, ffd.Entity):
                self.debug(f'{field.name} is an Entity reference. Adding a foreign key.')
                column_args.append(ForeignKey(f'{self._fqtn(t)}.{t.id_name()}'))

            c = Column(*column_args, **column_kwargs)
            self.debug(f'Adding column {str(c)}')
            args.append(c)

            idx = field.metadata.get('index')
            if idx is not None:
                self.debug(f'{field.name} is an index')
                if idx is True:
                    indexes[
                        f'idx_{entity.get_class_context()}_{inflection.tableize(entity.__name__)}_{field.name}'
                    ] = field.name
                else:
                    if idx not in indexes:
                        indexes[idx] = [field.name]
                    else:
                        indexes[idx].append(field.name)

        self._add_indexes(args, indexes, entity.get_class_context(), inflection.tableize(entity.__name__))

        try:
            table = Table(*args, **kwargs)
        except InvalidRequestError as e:
            if 'already defined' in str(e):
                self._stack.pop()
                return
            raise e

        properties = {}
        for k, v in relationships.items():
            kwargs = {}
            if v['other_side'] is not None:
                kwargs['back_populates'] = v['target_property']
            if v['metadata'].get('cascade') is not None:
                kwargs['cascade'] = v['metadata'].get('cascade')

            if v['this_side'] == 'one':
                properties[k] = relationship(v['target'], **kwargs)

            elif v['this_side'] == 'many':
                properties[k] = relationship(v['target'], **kwargs)

        for k, v in properties.items():
            print(v)
        mapper(entity, table, properties=properties)
        self._stack.pop()

    def create_functions(self):
        pass

    def _get_relationships(self, entity: Type[ffd.Entity], caller: Type[ffd.Entity] = None):
        relationships = {}
        annotations_ = get_type_hints(entity)
        for field in fields(entity):
            k = field.name
            v = annotations_[k]

            if k.startswith('_'):
                continue

            if isinstance(v, type) and issubclass(v, ffd.Entity):
                relationships[k] = {
                    'field_name': k,
                    'target': v,
                    'this_side': 'one',
                    'relationships': self._get_relationships(v, entity) if v is not caller else {},
                    'fqtn': self._fqtn(v),
                    'metadata': field.metadata,
                }

                relationships[k]['other_side'] = None
                relationships[k]['target_property'] = None
                for child_k, child_v in relationships[k]['relationships'].items():
                    if child_v is entity:
                        relationships[k]['other_side'] = 'one'
                        relationships[k]['target_property'] = child_k
                    elif ffd.is_type_hint(child_v) and child_v is List and ffd.get_args(child_v)[0] is entity:
                        relationships[k]['other_side'] = 'many'
                        relationships[k]['target_property'] = child_k

            elif ffd.is_type_hint(v):
                origin = ffd.get_origin(v)
                args = ffd.get_args(v)
                if origin is List and issubclass(args[0], ffd.Entity):
                    relationships[k] = {
                        'field_name': k,
                        'target': args[0],
                        'this_side': 'many',
                        'relationships': self._get_relationships(args[0], entity) if args[0] is not caller else {},
                        'fqtn': self._fqtn(args[0]),
                        'metadata': field.metadata,
                    }

                    relationships[k]['other_side'] = None
                    relationships[k]['target_property'] = None
                    for child_k, child_v in relationships[k]['relationships'].items():
                        if child_v is entity:
                            relationships[k]['other_side'] = 'one'
                            relationships[k]['target_property'] = child_k
                        elif ffd.is_type_hint(child_v) and child_v is List and ffd.get_args(child_v)[0] is entity:
                            relationships[k]['other_side'] = 'many'
                            relationships[k]['target_property'] = child_k

        return relationships

    @staticmethod
    def _add_indexes(args: list, indexes: dict, context: str, table: str):
        for k, v in indexes.items():
            if str(k).startswith('idx_'):
                args.append(Index(k, v))
            else:
                idx_args = [f'idx_{context}_{table}']
                for column in v:
                    idx_args[0] += f'_{column}'
                    idx_args.append(column)
                args.append(Index(*idx_args))

    @staticmethod
    def _fqtn(entity: Type[ffd.Entity]):
        return inflection.tableize(entity.get_fqn())

    def _add(self, entity: Union[ffd.Entity, List[ffd.Entity]]):
        list(map(
            lambda e: self._session.add(e),
            [entity] if not isinstance(entity, list) else entity
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

        data['relationships'] = self._get_relationships(entity_type)

        return self._generate_query(entity_type, f'{self._sql_prefix}/select.sql', data)

    def _all(self, entity_type: Type[ffd.Entity], criteria: ffd.BinaryOp = None, limit: int = None, offset: int = None,
             sort: Tuple[Union[str, Tuple[str, bool]]] = None, raw: bool = False, count: bool = False):
        self._cache = {}
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
                'criteria': ffd.Attr(entity_type.id_name()) == uuid,
                'relationships': self._get_relationships(entity_type),
            }
        ))

        if len(results) == 0:
            return None

        if len(results) > 1:
            raise ffd.MultipleResultsFound()

        return self._build_entity(entity_type, results[0])

    def _remove(self, entity: Union[ffd.Entity, List[ffd.Entity], Callable]):
        if isinstance(entity, (ffd.Entity, list)):
            list(map(
                lambda e: self._session.delete(e),
                [entity] if not isinstance(entity, list) else entity
            ))

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
                'data': self._data_fields(entity, add_new=True),
                'criteria': criteria
            }
        ))

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

    def get_table_columns(self, entity: Type[ffd.Entity]):
        return self._get_table_columns(entity)

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

    def create_index(self, entity: Type[ffd.Entity], index: Index):
        self.execute(
            *self._generate_query(entity, f'{self._sql_prefix}/add_index.sql', {'index': index})
        )

    def drop_index(self, entity: Type[ffd.Entity], index: Index):
        self.execute(
            *self._generate_query(entity, f'{self._sql_prefix}/drop_index.sql', {'index': index})
        )

    def _register_aggregate_references(self, entity: ffd.Entity):
        for k, v in self._get_relationships(entity.__class__).items():
            val = getattr(entity, k)
            if v['this_side'] == 'one':
                self._do_register_entity(val)
                self._register_aggregate_references(val)
            else:
                list(map(self._do_register_entity, val or []))
                list(map(self._register_aggregate_references, val or []))

    def _do_register_entity(self, entity):
        if isinstance(entity, ffd.AggregateRoot):
            self._registry(entity.__class__).register_entity(entity)

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

        ret = entity.from_dict(data)
        if version is not None:
            setattr(ret, '__ff_version', version)

        self._register_aggregate_references(ret)

        return ret

    def _cache_aggregate(self, type_: type, id_: str, value: ffd.AggregateRoot):
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
        print('create_schema')

    def _data_fields(self, entity: ffd.Entity, add_new: bool = False):
        ret = {}
        for f in self.get_entity_columns(entity.__class__):
            if f.name == 'document' and not hasattr(entity, 'document'):
                ret[f.name] = self._serialize_entity(entity, add_new=add_new)
            elif f.name == 'version':
                try:
                    ret['version'] = getattr(entity, '__ff_version')
                except AttributeError:
                    ret['version'] = 1
            elif inspect.isclass(f.type) and issubclass(f.type, ffd.AggregateRoot):
                try:
                    ret[f.name] = getattr(entity, f.name).id_value()
                except AttributeError:
                    if f.is_required:
                        raise ffd.RepositoryError(f"{f.name} is a required field, but no value is present.")
                    ret[f.name] = None
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
