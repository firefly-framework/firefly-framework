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

import hashlib
from abc import ABC, abstractmethod
from typing import List, TypeVar, Generic, Union, Callable, Optional

import firefly.domain as ffd

from ..service.logging.logger import LoggerAware
from ..value_object import GenericBase

T = TypeVar('T')


class Repository(Generic[T], GenericBase, LoggerAware, ABC):
    _serializer: ffd.Serializer = None

    def __init__(self):
        self._entity_hashes = {}
        self._entities = []
        self._deletions = []

    @abstractmethod
    def append(self, entity: T):
        pass

    @abstractmethod
    def remove(self, entity: T):
        pass

    @abstractmethod
    def find(self, exp: Union[str, Callable]) -> Optional[T]:
        pass

    @abstractmethod
    def filter(self, cb: Callable) -> List[T]:
        pass

    @abstractmethod
    def reduce(self, cb: Callable) -> Optional[T]:
        pass

    @abstractmethod
    def __iter__(self):
        pass

    @abstractmethod
    def __next__(self):
        pass

    @abstractmethod
    def __len__(self):
        pass

    @abstractmethod
    def __getitem__(self, item):
        pass

    def _get_search_criteria(self, cb: Callable) -> ffd.BinaryOp:
        return cb(ffd.EntityAttributeSpy(self._type()))

    def _get_hash(self, entity: ffd.Entity):
        return hashlib.md5(self._serializer.serialize(entity).encode('utf-8')).hexdigest()

    def _register_entity(self, entity: ffd.Entity):
        self._entity_hashes[id(entity)] = self._get_hash(entity)
        self._entities.append(entity)

    def _has_changed(self, entity: ffd.Entity):
        if id(entity) not in self._entity_hashes:
            return False
        return self._get_hash(entity) != self._entity_hashes[id(entity)]

    def _new_entities(self):
        ret = []
        for entity in self._entities:
            if id(entity) not in self._entity_hashes:
                ret.append(entity)
        return ret

    def _changed_entities(self):
        ret = []
        for entity in self._entities:
            if self._has_changed(entity):
                ret.append(entity)
        return ret

    @abstractmethod
    def commit(self):
        pass

    def reset(self):
        self._deletions = []
        self._entities = []
        self._entity_hashes = {}
