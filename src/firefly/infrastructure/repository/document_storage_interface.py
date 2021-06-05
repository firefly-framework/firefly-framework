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

from abc import ABC, abstractmethod
from typing import Type, List, Union, Callable, Tuple

import firefly.domain as ffd

from .abstract_storage_interface import AbstractStorageInterface


# noinspection PyDataclass
class DocumentStorageInterface(AbstractStorageInterface, ABC):
    _serializer: ffd.Serializer = None
    _registry: ffd.Registry = None
    _cache: dict = {}

    def __init__(self, **kwargs):
        self._tables_checked = []

    def disconnect(self):
        self._disconnect()

    def _disconnect(self):
        pass

    @abstractmethod
    def _add(self, entity: Union[ffd.Entity, List[ffd.Entity]]):
        pass

    @abstractmethod
    def _all(self, entity_type: Type[ffd.Entity], criteria: ffd.BinaryOp = None, limit: int = None, offset: int = None,
             sort: Tuple[Union[str, Tuple[str, bool]]] = None, raw: bool = False, count: bool = False):
        pass

    @abstractmethod
    def _find(self, uuid: str, entity_type: Type[ffd.Entity]):
        pass

    @abstractmethod
    def _remove(self, entity: Union[ffd.Entity, List[ffd.Entity], Callable]):
        pass

    @abstractmethod
    def _update(self, entity: ffd.Entity):
        pass

    @abstractmethod
    def _ensure_connected(self):
        pass

    def _check_prerequisites(self, entity: Type[ffd.Entity]):
        self._ensure_connected()

    def _build_entity(self, entity: Type[ffd.Entity], data, raw: bool = False):
        if raw is True:
            return self._serializer.deserialize(data)

        data = self._serializer.deserialize(data)

        for k, v in self._get_relationships(entity).items():
            if v['this_side'] == 'one':
                data[k] = self._registry(v['target']).find(data[k])
            elif v['this_side'] == 'many':
                data[k] = list(self._registry(v['target']).filter(
                    lambda ee: getattr(ee, v['target'].id_name()).is_in(data[k])
                ))

        return entity.from_dict(data)
