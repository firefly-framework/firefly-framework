from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, TypeVar, Generic

import firefly.domain as ffd

from ..value_object import GenericBase

T = TypeVar('T')


class Repository(Generic[T], GenericBase, ABC):
    @abstractmethod
    def all(self) -> List[T]:
        pass

    @abstractmethod
    def add(self, entity: T):
        pass

    @abstractmethod
    def remove(self, entity: T):
        pass

    @abstractmethod
    def update(self, entity: T):
        pass

    @abstractmethod
    def find(self, uuid) -> T:
        pass

    @abstractmethod
    def find_all_matching(self, criteria: ffd.BinaryOp) -> List[T]:
        pass

    @abstractmethod
    def find_one_matching(self, criteria: ffd.BinaryOp) -> T:
        pass
