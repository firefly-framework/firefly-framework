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
from datetime import datetime
from typing import List, Callable, Union, Tuple, Optional, get_type_hints
from uuid import UUID

import firefly.domain as ffd
import inflection
from firefly.domain.repository.repository import T, Repository
from firefly.domain.repository.search_criteria import Attr, AttributeString
from sqlalchemy import MetaData, text, String
from sqlalchemy.engine import Engine
from sqlalchemy.exc import InvalidRequestError, NoResultFound, MultipleResultsFound
from sqlalchemy.orm import Session, Query
from sqlalchemy.orm.exc import ObjectDeletedError

DEFAULT_LIMIT = 999999999999999999


class MISSING:
    pass


missing = MISSING()


class SqlalchemyRepository(Repository[T]):
    _map_entities: ffd.MapEntities = None
    _parse_relationships: ffd.ParseRelationships = None
    _convert_criteria: ffd.ConvertCriteriaToSqlalchemy = None
    _metadata: MetaData = None
    _session: Session = None
    _engine: Engine = None

    def __init__(self):
        super().__init__()

        self._entity_type = self._type()
        self._index = 0
        self._state = 'empty'
        self._query_details = {}

    def append(self, entity: Union[T, List[T], Tuple[T]], **kwargs):
        entities = entity if isinstance(entity, list) else [entity]
        for ee in entities:
            if hasattr(ee, 'created_on') and ee.created_on is None:
                ee.created_on = datetime.now()
            if hasattr(ee, 'updated_on'):
                ee.updated_on = datetime.now()
            self._session.add(ee)

    def remove(self, x: Union[T, List[T], Tuple[T], Callable, ffd.BinaryOp], **kwargs):
        # TODO handle case when x is SearchCriteria
        xs = x
        if not isinstance(x, (list, tuple)):
            xs = [x]

        for x in xs:
            try:
                if isinstance(x, ffd.Entity) and x in self._entities:
                    self._entities.remove(x)
            except ObjectDeletedError:
                pass
            finally:
                if hasattr(x, 'deleted_on'):
                    x.deleted_on = datetime.now()
                else:
                    self._session.delete(x)

    def find(self, x: Union[str, UUID, Callable, ffd.SearchCriteria], **kwargs) -> T:
        if isinstance(x, (str, UUID)):
            return self._session.query(self._entity_type).get(x)
        else:
            query = self._convert_criteria(
                self._entity_type,
                x if isinstance(x, ffd.SearchCriteria) else self._get_search_criteria(x),
                self._session.query(self._entity_type)
            )
            try:
                return query.one()
            except NoResultFound as e:
                raise ffd.NoResultFound() from e
            except MultipleResultsFound as e:
                raise ffd.MultipleResultsFound() from e

    def one(self, x: Union[str, UUID, Callable, ffd.SearchCriteria], **kwargs) -> T:
        results = list(self.filter(x, **kwargs))
        if len(results) == 0:
            raise ffd.NoResultFound()

        return results.pop()

    def filter(self, x: Union[Callable, ffd.BinaryOp], **kwargs) -> SqlalchemyRepository:
        self._query_details.update(kwargs)
        self._query_details['criteria'] = x

        return self.copy()

    def _do_filter(self, criteria: Union[Callable, ffd.BinaryOp] = None, limit: int = None, offset: int = None,
                   raw: bool = False, sort: tuple = None, count: bool = False) -> List[T]:

        query = self._session.query(self._entity_type)
        if criteria is not None:
            query = self._convert_criteria(
                self._entity_type,
                self._get_search_criteria(criteria) if not isinstance(criteria, ffd.BinaryOp) else criteria,
                query
            )

        if limit is not None:
            query.limit(limit)
        if offset is not None:
            query.offset(offset)
        if sort is not None:
            for s in sort:
                if isinstance(s, tuple):
                    field_, direction = s
                else:
                    field_ = s
                    direction = 'asc'
                c = getattr(self._entity_type, field_)
                query = query.order_by(getattr(c, direction)())

        return query.all() if count is False else query.count()

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
        pass  # TODO

    def destroy(self):
        pass  # TODO
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
        if self._query_details.get('raw', False) is True:
            return iter(self._load_data())
        self._load_data()
        return iter(list(self._entities))

    def __len__(self):
        params = self._query_details.copy()
        if 'criteria' in params and not isinstance(params['criteria'], ffd.BinaryOp):
            params['criteria'] = self._get_search_criteria(params['criteria'])
        return self._do_filter(count=True, **params)

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

        self._entities = results

    def commit(self, force_delete: bool = False):
        self._session.commit()

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
        self._session.close_all()

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
