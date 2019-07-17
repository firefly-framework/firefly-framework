from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TypeVar, Type

from .repository import Repository
from ..entity.entity import Entity

E = TypeVar('E', bound=Entity)


class RepositoryFactory(ABC):
    @abstractmethod
    def __call__(self, entity: Type[E]) -> Repository:
        pass
