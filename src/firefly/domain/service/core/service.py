from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional, Union

import firefly.domain as ffd


class Service(ABC):
    _bus: ffd.MessageBus = None

    @abstractmethod
    def __call__(self, **kwargs) -> Optional[Union[ffd.Message, object]]:
        pass

    def dispatch(self, message: ffd.Message):
        return self._bus.dispatch(message)

    @classmethod
    def get_arguments(cls) -> dict:
        return ffd.get_arguments(cls.__call__)
