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

from typing import Type, List, Union, Callable, Tuple

import firefly.domain as ffd
import inflection
from sqlalchemy import MetaData
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session


class SqlalchemyStorageInterface(ffd.HasMemoryCache, ffd.LoggerAware):
    _map_entities: ffd.MapEntities = None
    _parse_relationships: ffd.ParseRelationships = None
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

    def add(self, entity: Union[ffd.Entity, List[ffd.Entity]]):
        list(map(
            lambda e: self._session.add(e),
            [entity] if not isinstance(entity, list) else entity
        ))

    def all(self, entity_type: Type[ffd.Entity], criteria: ffd.BinaryOp = None, limit: int = None, offset: int = None,
             sort: Tuple[Union[str, Tuple[str, bool]]] = None, raw: bool = False, count: bool = False):
        return self._session.query(entity_type).all()

    def find(self, uuid: str, entity_type: Type[ffd.Entity]):
        return self._session.query(entity_type).get(uuid)

    def _remove(self, entity: Union[ffd.Entity, List[ffd.Entity], Callable]):
        if isinstance(entity, (ffd.Entity, list)):
            list(map(
                lambda e: self._session.delete(e),
                [entity] if not isinstance(entity, list) else entity
            ))

    def _update(self, entity: ffd.Entity):
        pass  # TODO
        # criteria = Attr(entity.id_name()) == entity.id_value()
        # try:
        #     criteria &= Attr('version') == getattr(entity, '__ff_version')
        # except AttributeError:
        #     pass
        #
        # return self._execute(*self._generate_query(
        #     entity,
        #     f'{self._sql_prefix}/update.sql',
        #     {
        #         'data': self._data_fields(entity, add_new=True),
        #         'criteria': criteria
        #     }
        # ))

    @staticmethod
    def _fqtn(entity: Type[ffd.Entity]):
        return inflection.tableize(entity.get_fqn())

    def _register_aggregate_references(self, entity: ffd.Entity):
        for k, v in self._parse_relationships(entity.__class__).items():
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

    def execute(self, sql: str, params: dict = None):
        self._execute(sql, params)
