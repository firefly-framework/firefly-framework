from __future__ import annotations

from abc import ABC, abstractmethod

from .repository import Repository


class Registry(ABC):
    @abstractmethod
    def __call__(self, type_: type) -> Repository:
        pass
