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

from abc import abstractmethod, ABC
from dataclasses import fields
from pprint import pprint
from typing import Type, Tuple, Union, List, get_type_hints, Dict

import firefly.domain as ffd
from firefly.infrastructure.repository.rdb_repository import DEFAULT_LIMIT

from ..rdb_storage_interface import RdbStorageInterface


# noinspection PyDataclass
class LegacyStorageInterface(RdbStorageInterface, ffd.LoggerAware, ABC):
    def _generate_select(self, entity_type: Type[ffd.Entity], criteria: ffd.BinaryOp = None, limit: int = None,
                         offset: int = None, sort: Tuple[Union[str, Tuple[str, bool]]] = None, count: bool = False):
        pruned_criteria = None
        indexes = [f.name for f in fields(entity_type)
                   if f.metadata.get('index') is True or f.metadata.get('id') is True]
        if criteria is not None:
            pruned_criteria = criteria.prune(indexes)
            data = {
                'columns': self._select_list(entity_type),
                'criteria': pruned_criteria,
                'count': count and (pruned_criteria == criteria),
            }
        else:
            data = {
                'columns': self._select_list(entity_type),
                'count': count,
            }

        sorted_in_db = False
        if sort is not None:
            sort_fields = []
            for s in sort:
                if str(s[0]) in indexes:
                    sort_fields.append(s)
            data['sort'] = sort_fields
            sorted_in_db = len(sort_fields) == len(sort)

        if (not sort or sorted_in_db) and (pruned_criteria is None or criteria == pruned_criteria):
            if limit is not None:
                data['limit'] = limit

            if offset is not None:
                data['offset'] = offset

        sql, params = self._generate_query(entity_type, f'{self._sql_prefix}/select.sql', data)

        return sql, params, pruned_criteria

    def _all(self, entity_type: Type[ffd.Entity], criteria: ffd.BinaryOp = None, limit: int = None, offset: int = None,
             sort: Tuple[Union[str, Tuple[str, bool]]] = None, raw: bool = False, count: bool = False):
        sql, params, pruned_criteria = self._generate_select(
            entity_type, criteria, limit=limit, offset=offset, sort=sort, count=count
        )

        results = self._execute(sql, params)

        ret = []
        if count and criteria == pruned_criteria:
            return results[0]['c']

        for row in results:
            self.debug('Result row: %s', dict(row))
            ret.append(self._build_entity(entity_type, row, raw=raw))

        if criteria != pruned_criteria:
            if limit is not None and offset is not None and sort is not None:
                self.warning('Paging being performed with non-indexed columns. This may lead to undesirable behavior.')
            ret = list(filter(lambda ee: criteria.matches(ee), ret))
            if count:
                ret = len(ret)

        indexes = [f.name for f in fields(entity_type)
                   if f.metadata.get('index') is True or f.metadata.get('id') is True]
        sorted_in_db = False

        if sort is not None:
            sort_fields = []
            for s in sort:
                if str(s[0]) in indexes:
                    sort_fields.append(s)
            sorted_in_db = len(sort_fields) == len(sort)

        if sort is not None and not sorted_in_db and isinstance(ret, list):
            def sort_keys(x):
                keys = []
                for ss in sort:
                    if len(ss) == 2 and ss[1]:
                        keys.append(-(getattr(x, str(ss[0]))))
                    else:
                        keys.append(getattr(x, str(ss[0])))
                return keys

            ret.sort(key=sort_keys)

        if (sort is not None and not sorted_in_db) and offset is not None and limit is not None:
            if limit == DEFAULT_LIMIT:
                return ret[offset:]
            else:
                return ret[offset:(offset + limit)]

        return ret

    def _build_entity(self, entity: Type[ffd.Entity], data, raw: bool = False):
        if self._map_all is True:
            types = get_type_hints(entity)
            for k, v in data.items():
                t = types[k]
                if ffd.is_type_hint(t):
                    if ffd.get_origin(t) is List:
                        t = list
                    elif ffd.get_origin(t) is Dict:
                        t = dict
                if isinstance(t, type) and issubclass(t, ffd.ValueObject):
                    t = dict

                if (t is dict or t is list) and isinstance(v, str):
                    data[k] = self._serializer.deserialize(v)

        return super()._build_entity(entity, data, raw)

    @abstractmethod
    def _execute(self, sql: str, params: dict = None):
        pass

    @abstractmethod
    def _ensure_connected(self):
        pass

    @abstractmethod
    def _disconnect(self):
        pass
