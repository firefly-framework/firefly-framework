from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, TypeVar, Generic

T = TypeVar('T')


class Repository(Generic[T], ABC):
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
    def find_all_by(self, **kwargs) -> List[T]:
        pass

    @abstractmethod
    def find_one_by(self, **kwargs) -> T:
        pass
