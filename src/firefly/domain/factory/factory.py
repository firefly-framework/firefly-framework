from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TypeVar, Generic
from ..value_object.generic_base import GenericBase

T = TypeVar('T')


class Factory(Generic[T], GenericBase, ABC):

    @abstractmethod
    def __call__(self, *args, **kwargs) -> T:
        pass
