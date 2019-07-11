from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Type, TypeVar

import firefly.domain as ffd

from ..messaging.message import Message
from ...service.messaging.system_bus import SystemBusAware

M = TypeVar('M', bound=Message)


class Port(ABC, SystemBusAware):
    target: Type[M] = None

    def __init__(self, target: Type[M]):
        self.target = target

    def handle(self, **kwargs):
        message = self._transform_input(**kwargs)
        if isinstance(message, ffd.Command):
            ret = self.invoke(message)
        elif isinstance(message, ffd.Query):
            ret = self.query(message)
        elif isinstance(message, ffd.Event):
            return self.dispatch(message)
        else:
            ret = self._execute_service(message)

        return self._transform_output(ret)

    def get_parameters(self):
        return self.target.get_parameters()

    def _execute_service(self, message: ffd.Message):
        return self.target(body=message.body(), **message.headers())

    @abstractmethod
    def _transform_input(self, **kwargs) -> ffd.Message:
        pass

    @abstractmethod
    def _transform_output(self, message: ffd.Message):
        pass
