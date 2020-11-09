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

from pprint import pprint
from typing import List, Callable, Union, Tuple, Optional

import firefly.domain as ffd
import firefly.infrastructure as ffi
import inflection
from firefly.domain.repository.repository import T

DEFAULT_LIMIT = 999999999999999999


class AbstractRepository(ffd.Repository[T]):
    def __init__(self, interface: ffi.AbstractStorageInterface):
        super().__init__()

        self._entity_type = self._type()
        self._interface = interface
        self._interface._repository = self
        self._index = 0
        self._state = 'empty'
        self._query_details = {}

    def append(self, entity: Union[T, List[T], Tuple[T]], **kwargs):
        if not isinstance(entity, (list, tuple)):
            entity = [entity]

        for e in entity:
            if e not in self._entities:
                self._entities.append(e)
                self.debug('Entity added to repository: %s', str(e))
        self._state = 'partial'

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
            entity = self._find_checked_out_entity(x)
            if entity is not None:
                return entity
            ret = self._interface.find(x, self._entity_type)
        else:
            if not isinstance(x, ffd.BinaryOp):
                x = self._get_search_criteria(x)
            results = self._interface.all(self._entity_type, x)
            if len(results) > 0:
                ret = results[0]

        if ret:
            self.register_entity(ret)
            if self._state == 'empty':
                self._state = 'partial'

        return ret

    def filter(self, x: Union[Callable, ffd.BinaryOp], **kwargs) -> AbstractRepository:
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
        self._interface.destroy(self._entity_type)

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

        if len(self._deletions) > 0:
            self.debug('Deleting %s', self._deletions)
            self._interface.remove(self._deletions, force=force_delete)

        new_entities = self._new_entities()
        if len(new_entities) > 0:
            self.debug('Adding %s', new_entities)
            self._interface.add(new_entities)

        for entity in self._changed_entities():
            self.debug('Updating %s', entity)
            self._interface.update(entity)
        self.debug('Done in commit()')

    def __repr__(self):
        return f'RdbRepository[{self._entity_type}]'

    def _find_checked_out_entity(self, id_: str):
        for entity in self._entities:
            if entity.id_value() == id_:
                return entity

    def reset(self):
        super().reset()
        self._query_details = {}
        self._state = 'empty'

    def migrate_schema(self):
        self._interface.create_schema(self._entity_type)
        self._interface.create_table(self._entity_type)

        entity_columns = self._interface.get_entity_columns(self._entity_type)
        table_columns = self._interface.get_table_columns(self._entity_type)

        for ec in entity_columns:
            if ec not in table_columns:
                self._interface.add_column(self._entity_type, ec)

        entity_indexes = self._interface.get_entity_indexes(self._entity_type)
        table_indexes = self._interface.get_table_indexes(self._entity_type)

        for ei in entity_indexes:
            if ei not in table_indexes:
                self._interface.create_index(self._entity_type, ei)
        for ti in table_indexes:
            if ti not in entity_indexes:
                self._interface.drop_index(self._entity_type, ti)


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
