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
from typing import List, TypeVar, Generic, Union, Callable, Optional, Tuple

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
        self._parent = None

    @abstractmethod
    def append(self, entity: Union[T, List[T], Tuple[T]], **kwargs):
        pass

    @abstractmethod
    def remove(self, x: Union[T, List[T], Tuple[T], Callable, ffd.BinaryOp], **kwargs):
        pass

    @abstractmethod
    def find(self, x: Union[str, Callable, ffd.BinaryOp], **kwargs) -> Optional[T]:
        pass

    @abstractmethod
    def filter(self, x: Union[Callable, ffd.BinaryOp], **kwargs) -> Repository:
        pass

    @abstractmethod
    def commit(self, **kwargs):
        pass

    @abstractmethod
    def sort(self, cb: Optional[Union[Callable, Tuple[Union[str, Tuple[str, bool]]]]], **kwargs):
        pass

    @abstractmethod
    def clear(self):
        pass

    @abstractmethod
    def destroy(self):
        pass

    def reset(self):
        self._deletions = []
        self._entities = []
        self._entity_hashes = {}

    def touch(self, entity: ffd.Entity):
        if entity.id_value() in self._entity_hashes:
            self._entity_hashes[entity.id_value()] = ''

    @abstractmethod
    def __iter__(self):
        pass

    @abstractmethod
    def __len__(self):
        pass

    @abstractmethod
    def __getitem__(self, item):
        pass

    def _get_search_criteria(self, cb: Union[Callable, ffd.BinaryOp]) -> ffd.BinaryOp:
        if isinstance(cb, ffd.BinaryOp):
            return cb
        return cb(ffd.EntityAttributeSpy(self._type()))

    def _get_hash(self, entity: ffd.Entity):
        return hashlib.md5(self._serializer.serialize(entity.to_dict(force_all=True)).encode('utf-8')).hexdigest()

    def register_entity(self, entity: ffd.Entity):
        self._entity_hashes[entity.id_value()] = self._get_hash(entity)
        self._entities.append(entity)
        if self._parent is not None:
            self._parent.register_entity(entity)

    def _has_changed(self, entity: ffd.Entity):
        if entity.id_value() not in self._entity_hashes:
            return False
        return self._get_hash(entity) != self._entity_hashes[entity.id_value()]

    def _new_entities(self):
        return [e for e in self._entities if e.id_value() not in self._entity_hashes]

    def _changed_entities(self):
        return [e for e in self._entities if self._has_changed(e)]
