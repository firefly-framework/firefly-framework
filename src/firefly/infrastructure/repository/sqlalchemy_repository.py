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
from typing import List, Callable, Union, Tuple, Optional, get_type_hints

import firefly.domain as ffd
import firefly.infrastructure as ffi
import inflection
from firefly.domain.repository.repository import T, Repository
from sqlalchemy import MetaData
from sqlalchemy.orm import Session

DEFAULT_LIMIT = 999999999999999999


class SqlalchemyRepository(Repository[T]):
    _sqlalchemy_metadata: MetaData = None
    _sqlalchemy_session: Session = None

    def __init__(self, interface: ffi.SqlalchemyStorageInterface, table_name: str = None):
        super().__init__()

        self._entity_type = self._type()
        self._table = table_name or inflection.tableize(self._entity_type.get_fqn())
        self._interface = interface
        self._index = 0
        self._state = 'empty'
        self._query_details = {}

    def execute(self, sql: str, params: dict = None):
        self._interface.execute(sql, params)

    def append(self, entity: Union[T, List[T], Tuple[T]], **kwargs):
        entities = entity if isinstance(entity, list) else [entity]

        types = get_type_hints(entities[0].__class__)
        for entity in entities:
            missing = []
            for field_ in fields(entity):
                is_required = field_.metadata.get('required', False) is True
                has_no_value = getattr(entity, field_.name) is None
                is_entity = inspect.isclass(types[field_.name]) and issubclass(types[field_.name], ffd.Entity)
                if is_required and has_no_value and is_entity:
                    missing.append(field_.name)
            if len(missing) > 0:
                raise TypeError(f"Can't persist {entity.__class__.__name__}, missing {len(missing)} "
                                f"required argument(s): {', '.join(missing)}")

        list(map(lambda ee: self._sqlalchemy_session.add(ee), entities))

    def remove(self, x: Union[T, List[T], Tuple[T], Callable, ffd.BinaryOp], **kwargs):
        if self._parent is not None:
            self._parent.remove(x)

        xs = x
        if not isinstance(x, (list, tuple)):
            xs = [x]

        for x in xs:
            self.debug('Entity removed from repository: %s', str(x))
            self._deletions.append(x)
            if isinstance(x, ffd.Entity) and x in self._entities:
                self._entities.remove(x)

    def find(self, x: Union[str, Callable, ffd.BinaryOp], **kwargs) -> T:
        ret = None
        if isinstance(x, str):
            ret = self._interface.find(x, self._entity_type)
        else:
            if not isinstance(x, ffd.BinaryOp):
                x = self._get_search_criteria(x)
            entity = self._find_checked_out_entity(x)
            if entity is not None:
                return entity
            results = self._interface.all(self._entity_type, x)
            if len(results) > 0:
                ret = results[0]

        return ret

    def filter(self, x: Union[Callable, ffd.BinaryOp], **kwargs) -> SqlalchemyRepository:
        self._query_details.update(kwargs)
        self._query_details['criteria'] = x

        return self.copy()

    def _do_filter(self, criteria: Union[Callable, ffd.BinaryOp], limit: int = None, offset: int = None,
                   raw: bool = False, sort: tuple = None) -> List[T]:
        if criteria is not None:
            criteria = self._get_search_criteria(criteria) if not isinstance(criteria, ffd.BinaryOp) else criteria
        if self._state == 'full':
            entities = list(filter(lambda e: criteria.matches(e), self._entities))
        else:
            entities = self._interface.all(
                self._entity_type, criteria=criteria, limit=limit, offset=offset, raw=raw, sort=sort
            )

            merged = []
            for entity in entities:
                if entity in self._entities:
                    merged.append(next(e for e in self._entities if e == entity))
                else:
                    merged.append(entity)
                    if raw is False:
                        self.register_entity(entity)
            if self._state == 'empty':
                self._state = 'partial'
            entities = merged
        return entities

    def sort(self, cb: Optional[Union[Callable, Tuple[Union[str, Tuple[str, bool]]]]] = None, **kwargs):
        if cb is None and 'key' in kwargs:
            return list(self).sort(**kwargs)

        if not isinstance(cb, tuple):
            cb = cb(ffd.EntityAttributeSpy(self._entity_type))
            if not isinstance(cb, tuple):
                cb = [(cb,)]
        self._query_details['sort'] = cb

        return self.copy()

    def clear(self):
        self._interface.clear(self._entity_type)

    def destroy(self):
        pass
        # self._sqlalchemy_metadata.drop_all()

    def copy(self):
        ret = self.__class__()
        ret._query_details = self._query_details.copy()
        ret._entities = []
        ret._entity_hashes = {}
        ret._deletions = []
        ret._parent = self

        deletions = self._deletions
        entities = self._new_entities()
        self.reset()
        self._deletions = deletions
        self._entities = entities

        return ret

    def __iter__(self):
        if 'raw' in self._query_details and self._query_details['raw'] is True:
            return iter(self._load_data())
        self._load_data()
        return iter(list(self._entities))

    def __len__(self):
        params = self._query_details.copy()
        if 'criteria' in params and not isinstance(params['criteria'], ffd.BinaryOp):
            params['criteria'] = self._get_search_criteria(params['criteria'])
        return self._interface.all(self._entity_type, count=True, **params)

    def __getitem__(self, item):
        if isinstance(item, slice):
            if item.start is not None:
                self._query_details['offset'] = item.start
            if item.stop is not None:
                self._query_details['limit'] = (item.stop - item.start) + 1
            else:
                self._query_details['limit'] = DEFAULT_LIMIT
        else:
            if len(self._entities) > item:
                return self._entities[item]
            self._query_details['offset'] = item
            self._query_details['limit'] = 1

        if 'raw' in self._query_details and self._query_details['raw'] is True:
            return self._load_data()

        self._load_data()

        if isinstance(item, slice):
            return self._entities
        elif len(self._entities) > 0:
            return self._entities[-1]

    def _load_data(self):
        query_details = self._query_details

        if 'criteria' not in query_details:
            query_details['criteria'] = None

        results = self._do_filter(**query_details)
        if 'raw' in query_details and query_details['raw'] is True:
            return results

        if isinstance(results, list):
            for entity in results:
                if entity not in self._entities:
                    self.register_entity(entity)

    def commit(self, force_delete: bool = False):
        self.debug('commit() called in %s', str(self))
        self._sqlalchemy_session.commit()

    def __repr__(self):
        return f'RdbRepository[{self._entity_type}]'

    def _find_checked_out_entity(self, x: Union[str, ffd.BinaryOp]):
        for entity in self._entities:
            if isinstance(x, str) and entity.id_value() == x:
                return entity
            elif isinstance(x, ffd.BinaryOp) and x.matches(entity):
                return entity

    def reset(self):
        super().reset()
        self._query_details = {}
        self._state = 'empty'
        self._interface._cache = {}

    def migrate_schema(self):
        pass
        # self._interface.create_functions()
        # self._interface.create_schema(self._entity_type)
        # self._interface.create_table(self._entity_type)
        #
        # entity_columns = self._interface.get_entity_columns(self._entity_type)
        # table_columns = self._interface.get_table_columns(self._entity_type)
        #
        # for ec in entity_columns:
        #     if ec not in table_columns:
        #         self._interface.add_column(self._entity_type, ec)
        #
        # entity_indexes = self._interface.get_entity_indexes(self._entity_type)
        # table_indexes = self._interface.get_table_indexes(self._entity_type)
        #
        # for ei in entity_indexes:
        #     if ei not in table_indexes:
        #         self._interface.create_index(self._entity_type, ei)
        # for ti in table_indexes:
        #     if ti not in entity_indexes:
        #         self._interface.drop_index(self._entity_type, ti)


class Index(ffd.ValueObject):
    name: str = ffd.optional()
    table: str = ffd.optional()
    columns: List[str] = ffd.list_()
    unique: bool = ffd.optional(default=False)

    def __post_init__(self):
        if self.name is None:
            self.name = f'idx_{self.table}_{"_".join(self.columns)}'

    def __eq__(self, other):
        return self.name == other.name


class Column(ffd.ValueObject):
    name: str = ffd.required()
    type: str = ffd.required()
    length: int = ffd.optional()
    is_id: bool = ffd.optional(default=False)
    is_indexed: bool = ffd.optional(default=False)
    is_required: bool = ffd.optional(default=False)
    default: any = ffd.optional()

    @property
    def string_type(self):
        return str(self.type.__name__)

    def index(self):
        return self.is_id or (self.is_indexed and self.type is str)

    def __eq__(self, other):
        return self.name == other.name