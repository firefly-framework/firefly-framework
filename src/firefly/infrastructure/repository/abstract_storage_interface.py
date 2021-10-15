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
from abc import ABC, abstractmethod
from dataclasses import fields
from datetime import datetime
from typing import Type, get_type_hints, List, Union, Callable, Dict, Tuple

import firefly.domain as ffd
import inflection
# noinspection PyDataclass
from jinjasql import JinjaSql

from .rdb_repository import Index, Column


# noinspection PyDataclass
class AbstractStorageInterface(ffd.LoggerAware, ABC):
    _serializer: ffd.Serializer = None
    _registry: ffd.Registry = None
    _cache: dict = {}

    def disconnect(self):
        self._disconnect()

    def _disconnect(self):
        pass

    def add(self, entity: Union[ffd.Entity, List[ffd.Entity]]):
        self._check_prerequisites(entity.__class__)
        return self._add(entity)

    @abstractmethod
    def _add(self, entity: Union[ffd.Entity, List[ffd.Entity]]):
        pass

    def all(self, entity_type: Type[ffd.Entity], criteria: ffd.BinaryOp = None, limit: int = None, offset: int = None,
            sort: Tuple[Union[str, Tuple[str, bool]]] = None, raw: bool = False, count: bool = False):
        self._check_prerequisites(entity_type)
        return self._all(entity_type, criteria, limit, offset, raw=raw, count=count, sort=sort)

    @abstractmethod
    def _all(self, entity_type: Type[ffd.Entity], criteria: ffd.BinaryOp = None, limit: int = None, offset: int = None,
             sort: Tuple[Union[str, Tuple[str, bool]]] = None, raw: bool = False, count: bool = False):
        pass

    def find(self, uuid: str, entity_type: Type[ffd.Entity]):
        self._check_prerequisites(entity_type)
        return self._find(uuid, entity_type)

    @abstractmethod
    def _find(self, uuid: str, entity_type: Type[ffd.Entity]):
        pass

    def remove(self, entity: Union[ffd.Entity, List[ffd.Entity], Callable], force: bool = False):
        self._check_prerequisites(entity.__class__)
        deletions = []

        entities = entity
        if not isinstance(entity, list):
            entities = [entity]

        for entity in entities:
            if hasattr(entity, 'deleted_on') and not force:
                entity.deleted_on = datetime.now()
                self._update(entity)
            else:
                deletions.append(entity)

        if len(deletions) > 0:
            self._remove(deletions)

    @abstractmethod
    def _remove(self, entity: Union[ffd.Entity, List[ffd.Entity], Callable]):
        pass

    def update(self, entity: ffd.Entity):
        self._check_prerequisites(entity.__class__)
        if hasattr(entity, 'updated_on'):
            entity.updated_on = datetime.now()
        return self._update(entity)

    @abstractmethod
    def _update(self, entity: ffd.Entity):
        pass

    @abstractmethod
    def _ensure_connected(self):
        pass

    @abstractmethod
    def clear(self, entity: Type[ffd.Entity]):
        pass

    @abstractmethod
    def destroy(self, entity: Type[ffd.Entity]):
        pass

    def _check_prerequisites(self, entity: Type[ffd.Entity]):
        self._ensure_connected()

    @abstractmethod
    def _build_entity(self, entity: Type[ffd.Entity], data, raw: bool = False):
        pass

    def _get_relationships(self, entity: Type[ffd.Entity]):
        relationships = {}
        annotations_ = get_type_hints(entity)
        for k, v in annotations_.items():
            if k.startswith('_'):
                continue
            if isinstance(v, type) and issubclass(v, ffd.AggregateRoot):
                relationships[k] = {
                    'field_name': k,
                    'target': v,
                    'this_side': 'one',
                }
            elif ffd.is_type_hint(v):
                origin = ffd.get_origin(v)
                args = ffd.get_args(v)
                if origin is List and issubclass(args[0], ffd.AggregateRoot):
                    relationships[k] = {
                        'field_name': k,
                        'target': args[0],
                        'this_side': 'many',
                    }
        return relationships

    def _get_relationship(self, entity: Type[ffd.Entity], inverse_entity: Type[ffd.Entity]):
        relationships = self._get_relationships(entity)
        for k, v in relationships.items():
            if v['target'] == inverse_entity:
                return v

    def _load_relationships(self, entity: Type[ffd.Entity], data: dict):
        for k, v in self._get_relationships(entity).items():
            if v['this_side'] == 'one':
                if data[k] is not None:
                    data[k] = self._registry(v['target']).find(data[k])
            elif v['this_side'] == 'many':
                data[k] = list(self._registry(v['target']).filter(
                    lambda ee: getattr(ee, v['target'].id_name()).is_in(data[k])
                ))

        return data

    def _serialize_entity(self, entity: ffd.Entity):
        relationships = self._get_relationships(entity.__class__)
        if len(relationships.keys()) > 0:
            obj = entity.to_dict(force_all=True, skip=list(relationships.keys()))
            for k, v in relationships.items():
                if v['this_side'] == 'one':
                    try:
                        obj[k] = getattr(entity, k).id_value()
                    except AttributeError:
                        obj[k] = None
                elif v['this_side'] == 'many':
                    obj[k] = []
                    for f in getattr(entity, k):
                        try:
                            obj[k].append(f.id_value())
                        except AttributeError:
                            obj[k].append(None)
        else:
            obj = entity.to_dict(force_all=True)

        return self._serializer.serialize(obj)
