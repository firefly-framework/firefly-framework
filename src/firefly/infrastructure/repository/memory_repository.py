from __future__ import annotations

from typing import List

import firefly.domain as ffd
from firefly.domain.repository.repository import T


class MemoryRepository(ffd.Repository[T]):
    def __init__(self):
        self.entities = []

    def all(self) -> List[T]:
        return self.entities

    def add(self, entity: T):
        self.entities.append(entity)

    def remove(self, entity: T):
        self.entities.remove(entity)

    def update(self, entity: T):
        self.remove(entity)
        self.add(entity)

    def find(self, uuid) -> T:
        for e in self.entities:
            if e.id_value() == uuid:
                return e

    def find_all_matching(self, criteria: ffd.BinaryOp) -> List[T]:
        ret = []
        for entity in self.entities:
            if criteria.matches(entity):
                ret.append(entity)

        return ret

    def find_one_matching(self, criteria: ffd.BinaryOp) -> T:
        for entity in self.entities:
            if criteria.matches(entity):
                return entity

        return None
