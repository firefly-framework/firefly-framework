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
from typing import Type, List, Optional, get_type_hints, get_origin, get_args

import firefly.domain as ffd
import inflection
from firefly.domain.utils import is_type_hint
from sqlalchemy import MetaData, Table, Column, ForeignKey, Text, String, Float, Integer, DateTime, Date, Boolean, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.engine import Engine
from sqlalchemy.exc import ProgrammingError, InvalidRequestError, OperationalError
from sqlalchemy.orm import relationship, mapper
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.sql.ddl import CreateSchema

from .parse_relationships import ParseRelationships

TYPE_MAPPINGS = {
    float: lambda: Float(48),
    int: lambda: Integer,
    datetime: lambda: DateTime,
    date: lambda: Date,
    bool: lambda: Boolean,
}


class MapEntities(ffd.HasMemoryCache, ffd.LoggerAware):
    """
    TODO: Add support for association objects?
    TODO: Hash mapping?
    """
    _parse_relationships: ParseRelationships = None
    _engine: Engine = None
    _metadata: MetaData = None
    _kernel: ffd.Kernel = None
    _stack: list = None
    _db_type: str = None

    def __call__(self, entities: Optional[List[Type[ffd.Entity]]] = None):
        if self._engine is None:
            return

        self._stack = []
        if entities is None:
            entities = self._kernel.get_entities()

        if self._logger is None:
            self._logger = self._kernel.logger

        self._generated_schemas = []
        self._add_relationship_metadata(entities)
        list(map(lambda e: self._map_entity(e), entities))

    def _add_relationship_metadata(self, entities: List[Type[ffd.Entity]]):
        for entity in entities:
            for k, v in self._parse_relationships(entity).items():
                if v['this_side'] == 'many' and v['target_property'] not in v['relationships']:
                    key = f'mappings.{inflection.underscore(v["target"].__name__)}'
                    mappings = self._cache_get(key) or {}
                    mappings[f'{inflection.underscore(entity.__name__)}_id'] = entity
                    self._cache_set(key, mappings)

    def _map_entity(self, entity: Type[ffd.Entity]):
        self.debug(f'_map_entity: {entity}')
        if entity in self._stack:
            self.debug(f'Entity {entity} is already mapped or being mapped. Bailing out.')
            return
        self._stack.append(entity)

        schema, table_name = self._fqtn(entity).split('.')
        try:
            if entity not in self._generated_schemas:
                self._generated_schemas.append(entity)
                self._engine.execute(CreateSchema(schema))
        except ProgrammingError as e:
            if self._db_type == 'sqlite':
                schema = None
            elif 'already exists' not in str(e):
                raise e
        except OperationalError:
            pass
        args = [table_name, self._metadata]
        kwargs = {
            'schema': schema,
        }
        types = get_type_hints(entity)
        indexes = {}
        relationships = self._parse_relationships(entity)
        join_tables = {}
        mappings = self._cache_get(f'mappings.{inflection.underscore(entity.__name__)}')
        o2o_owner = '__one_to_one_owner_{}'

        for field in fields(entity):
            if field.name.startswith('_'):
                self.debug(f'Skipping private property {field.name}')
                continue

            t = types[field.name]
            column_args = [field.name]
            column_kwargs = {}

            if inspect.isclass(t) and issubclass(t, ffd.Entity):
                self._map_entity(t)

                try:
                    other_side_is_owner = getattr(
                        relationships[field.name]['target'], o2o_owner.format(
                            relationships[field.name]['target'].__name__
                        )
                    ) is True
                except AttributeError:
                    other_side_is_owner = False

                if other_side_is_owner:
                    self.debug('Other side is the owner')
                    continue

                if issubclass(entity, ffd.AggregateRoot) and \
                        not issubclass(relationships[field.name]['target'], ffd.AggregateRoot) and \
                        relationships[field.name]['other_side'] == 'one':
                    self.debug('This class is an Aggregate in a 1-to-1, but the other side is an Entity. Skipping.')
                    continue

                entities = [entity.__name__, relationships[field.name]['target'].__name__]
                entities.sort()
                if entities[1] == entity.__name__:
                    self.debug('Defaulting to alphabetical ordering. Skipping.')
                    continue

                column_args[0] = column_args[0] + '_id'
                column_args.append(UUID)
                self.debug(f"Setting {o2o_owner.format(relationships[field.name]['target'].__name__)} to True")
                setattr(
                    entity,
                    o2o_owner.format(relationships[field.name]['target'].__name__),
                    True
                )

            elif is_type_hint(t) and get_origin(t) is list:
                self._map_entity(get_args(t)[0])
                if relationships[field.name]['target_property'] is not None and \
                        relationships[field.name]['other_side'] == 'many':
                    names = [table_name, self._fqtn(relationships[field.name]['target']).split('.')[-1]]
                    names.sort()

                    if names[0] == table_name:
                        left_col = relationships[field.name]["target"].id_name()
                        right_col = entity.id_name()
                        left_table = names[0]
                        right_table = names[1]
                    else:
                        left_col = entity.id_name()
                        right_col = relationships[field.name]["target"].id_name()
                        left_table = names[1]
                        right_table = names[0]

                    join_tables[field.name] = Table(
                        f'{names[0]}_{names[1]}',
                        self._metadata,
                        Column(
                            inflection.underscore(entity.__name__), UUID, ForeignKey(
                                f'{schema}.{left_table}.{left_col}'
                            )
                        ),
                        Column(
                            inflection.underscore(relationships[field.name]['target'].__name__), UUID, ForeignKey(
                                f'{schema}.{right_table}.{right_col}'
                            )
                        ),
                        extend_existing=True,
                        schema=schema
                    )
                self.debug(f'property {field.name} is a list... not adding any columns')
                continue

            elif is_type_hint(t) and get_origin(t) is dict:
                a = get_args(t)
                if inspect.isclass(a[1]) and issubclass(a[1], ffd.Entity):
                    continue
                else:
                    column_args.append(JSONB)

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
                self.debug(
                    f'{field.name} is an Entity reference. Adding a foreign key. ({self._fqtn(t)}.{t.id_name()})'
                )
                column_args.append(ForeignKey(f'{self._fqtn(t)}.{t.id_name()}'))

            column_kwargs.update(field.metadata.get('sa_column_kwargs', {}))
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

        if mappings is not None:
            for k, v in mappings.items():
                args.append(Column(k, UUID, ForeignKey(f'{schema}.{inflection.tableize(v.__name__)}.{v.id_name()}')))

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
            if v['this_side'] == 'hash':
                kwargs['collection_class'] = attribute_mapped_collection(
                    v['metadata'].get('sa_relationship_kwargs', {}).get('attr_name', v['target'].id_name())
                )

            if (v['this_side'] == 'many' and v['other_side'] == 'one') or \
                    (getattr(v['target'], o2o_owner.format(entity.__name__), False) is True):
                kwargs['cascade'] = 'all, delete-orphan'

            kwargs.update(v['metadata'].get('sa_relationship_kwargs', {}))
            if v['this_side'] == 'one':
                if v['other_side'] == 'one' and entity.__name__ != 'Settings':
                    kwargs['uselist'] = False

                self.debug(f'REL: ({entity.__name__}) {entity.__name__}.{k} = relationship({v["target"]}, {kwargs})')
                properties[k] = relationship(v['target'], **kwargs)

            elif v['this_side'] == 'many':
                if v['other_side'] == 'many':
                    kwargs['secondary'] = join_tables[k]
                self.debug(f'REL: ({entity.__name__}) {entity.__name__}.{k} = relationship({v["target"]}, {kwargs})')
                properties[k] = relationship(v['target'], **kwargs)

        setattr(entity, '__mapper__', mapper(entity, table, properties=properties))
        setattr(entity, '__table__', table)
        self._stack.pop()

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
