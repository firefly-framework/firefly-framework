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

from typing import List, Callable, Union, Tuple

import firefly.domain as ffd
import firefly.infrastructure as ffi
import inflection
from firefly.domain.repository.repository import T


class RdbRepository(ffd.Repository[T]):
    def __init__(self, interface: ffi.RdbStorageInterface, table_name: str = None):
        super().__init__()

        self._entity_type = self._type()
        self._table = table_name or inflection.tableize(self._entity_type.get_fqn())
        self._interface = interface
        self._index = 0
        self._state = 'empty'
        self._page_details = {}

    def execute(self, sql: str, params: dict = None):
        self._interface.execute(sql, params)

    def append(self, entity: T, **kwargs):
        self.debug('Entity added to repository: %s', str(entity))
        if entity not in self._entities:
            self._entities.append(entity)
        self._state = 'partial'

    def remove(self, x: Union[T, Callable, ffd.BinaryOp], **kwargs):
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
            self._register_entity(ret)
            if self._state == 'empty':
                self._state = 'partial'

        return ret

    def filter(self, x: Union[Callable, ffd.BinaryOp], **kwargs) -> RdbRepository:
        self._page_details.update(kwargs)
        self._page_details['criteria'] = x

        return self

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
                    self._register_entity(entity)
            if self._state == 'empty':
                self._state = 'partial'
            entities = merged
        return entities

    def sort(self, cb: Union[Callable, Tuple[Union[str, Tuple[str, bool]]]]):
        if not isinstance(cb, tuple):
            cb = cb(ffd.EntityAttributeSpy(self._entity_type))
            if not isinstance(cb, tuple):
                cb = [(cb,)]
        self._page_details['sort'] = cb

        return self

    def clear(self):
        self._interface.clear(self._entity_type)

    def destroy(self):
        self._interface.destroy(self._entity_type)

    def __iter__(self):
        self._load_data()
        return iter(list(self._entities))

    def __len__(self):
        return self._interface.all(self._entity_type, count=True, **self._page_details)

    def __getitem__(self, item):
        if isinstance(item, slice):
            self._page_details['offset'] = item.start
            self._page_details['limit'] = (item.stop - item.start) + 1
        else:
            self._page_details['offset'] = item
            self._page_details['limit'] = 1

        self._load_data()

        if isinstance(item, slice):
            return self._entities
        elif len(self._entities) > 0:
            return self._entities[0]

    def _load_data(self):
        page_details = self._page_details
        self.reset()

        if 'criteria' not in page_details:
            page_details['criteria'] = None

        results = self._do_filter(**page_details)

        if isinstance(results, list):
            for entity in results:
                if entity not in self._entities:
                    self._register_entity(entity)

    def commit(self, force_delete: bool = False):
        self.debug('commit() called in %s', str(self))
        for entity in self._deletions:
            self.debug('Deleting %s', entity)
            self._interface.remove(entity, force=force_delete)

        for entity in self._new_entities():
            self.debug('Adding %s', entity)
            self._interface.add(entity)

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
        self._page_details = {}
        self._state = 'empty'

    def migrate_schema(self):
        self._interface.create_database(self._entity_type)
        self._interface.create_table(self._entity_type)

        entity_columns = self._interface.get_entity_columns(self._entity_type)
        table_columns = self._interface.get_table_columns(self._entity_type)

        for ec in entity_columns:
            if ec not in table_columns:
                self._interface.add_column(self._entity_type, ec)
        for tc in table_columns:
            if tc not in entity_columns:
                self._interface.drop_column(self._entity_type, tc)

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


class Column(ffd.ValueObject):
    name: str = ffd.required()
    type: str = ffd.required()
    length: int = ffd.optional()
    is_id: bool = ffd.optional(default=False)

    @property
    def string_type(self):
        return str(self.type)

    def __eq__(self, other):
        return self.name == other.name
