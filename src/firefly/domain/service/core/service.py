from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional, Union

import firefly.domain as ffd


class Service(ABC):
    bus: ffd.MessageBus = None

    @abstractmethod
    def __call__(self, **kwargs) -> Optional[Union[ffd.Message, object]]:
        pass

    def dispatch(self, event: ffd.Event):
        return self.bus.dispatch(event)

    @classmethod
    def with_(cls, **kwargs) -> ffd.Command:
        return ffd.Command(service_name=cls.__name__, **kwargs)

    @classmethod
    def get_arguments(cls) -> dict:
        return ffd.get_arguments(cls.__call__)
