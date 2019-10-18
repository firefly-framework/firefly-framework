from __future__ import annotations

from typing import List

import firefly.domain as ffd
import firefly.infrastructure as ffi
import inflection
from firefly.domain.repository.repository import T


class DbApiObjectRepository(ffd.Repository[T]):
    def __init__(self, interface: ffi.DbApiStorageInterface):
        self._entity_type = self._type()
        self._table = inflection.tableize(self._entity_type.__name__)
        self._interface = interface

    def all(self) -> List[T]:
        return self._interface.all(self._entity_type)

    def add(self, entity: T):
        self._interface.add(entity)

    def remove(self, entity: T):
        self._interface.remove(entity)

    def update(self, entity: T):
        self._interface.update(entity)

    def find(self, uuid) -> T:
        return self._interface.find(uuid, self._entity_type)

    def find_all_matching(self, criteria: ffd.BinaryOp) -> List[T]:
        return self._interface.all(self._entity_type, criteria=criteria)

    def find_one_matching(self, criteria: ffd.BinaryOp) -> T:
        return self._interface.all(self._entity_type, criteria=criteria, limit=1)
