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
from typing import Type, Tuple, Union

import firefly.domain as ffd

from ..rdb_storage_interface import RdbStorageInterface


# noinspection PyDataclass
class LegacyStorageInterface(RdbStorageInterface, ffd.LoggerAware, ABC):
    def _add(self, entity: ffd.Entity):
        return self._execute(*self._generate_query(
            entity,
            f'{self._sql_prefix}/insert.sql',
            {'data': self._data_fields(entity)}
        ))

    def _find(self, uuid: str, entity_type: Type[ffd.Entity]):
        results = self._execute(*self._generate_query(
            entity_type,
            f'{self._sql_prefix}/select.sql',
            {
                'columns': ['document'],
                'criteria': ffd.Attr(entity_type.id_name()) == uuid
            }
        ))
        if len(results) > 0:
            return self._build_entity(entity_type, results[0])

    def _remove(self, entity: Union[ffd.Entity, ffd.BinaryOp]):
        self._execute(*self._generate_query(entity, f'{self._sql_prefix}/delete.sql', {
            'criteria': entity if isinstance(entity, ffd.BinaryOp) else ffd.Attr(entity.id_name()) == entity.id_value()
        }))

    def _update(self, entity: ffd.Entity):
        return self._execute(*self._generate_query(
            entity,
            f'{self._sql_prefix}/update.sql',
            {
                'data': self._data_fields(entity),
                'criteria': ffd.Attr(entity.id_name()) == entity.id_value()
            }
        ))

    def _generate_select(self, entity_type: Type[ffd.Entity], criteria: ffd.BinaryOp = None, limit: int = None,
                         offset: int = None, sort: Tuple[Union[str, Tuple[str, bool]]] = None, count: bool = False):
        pruned_criteria = None
        indexes = [f.name for f in fields(entity_type) if f.metadata.get('index') is True]
        if criteria is not None:
            pruned_criteria = criteria.prune(indexes)
            data = {
                'columns': ['document'],
                'criteria': pruned_criteria,
                'count': count and (pruned_criteria == criteria),
            }
        else:
            data = {
                'columns': ['document'],
                'count': count,
            }

        sorted_in_db = False
        if sort is not None:
            sort_fields = []
            for s in sort:
                if s[0] in indexes:
                    sort_fields.append(s)
            data['sort'] = sort_fields
            sorted_in_db = len(sort_fields) == len(sort)

        if not sort or sorted_in_db:
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

        indexes = [f.name for f in fields(entity_type) if f.metadata.get('index') is True]
        sorted_in_db = False
        if sort is not None:
            sort_fields = []
            for s in sort:
                if s[0] in indexes:
                    sort_fields.append(s)
            sorted_in_db = len(sort_fields) == len(sort)

        if sort is not None and not sorted_in_db:
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
            return ret[offset:(offset + limit)]

        return ret

    def _migrate_table(self, entity: Type[ffd.Entity]):
        pass

    @abstractmethod
    def _build_entity(self, entity: Type[ffd.Entity], data, raw: bool = False):
        pass

    @abstractmethod
    def _execute(self, sql: str, params: dict = None):
        pass

    @abstractmethod
    def _ensure_connected(self):
        pass

    @abstractmethod
    def _disconnect(self):
        pass
