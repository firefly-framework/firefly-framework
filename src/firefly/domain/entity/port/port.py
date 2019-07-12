from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Type, TypeVar

import firefly.domain as ffd

from ..messaging.message import Message
from ...service.messaging.system_bus import SystemBusAware

M = TypeVar('M', bound=Message)


class Port(ABC, SystemBusAware):
    target: Type[M] = None
    config: dict = None

    def __init__(self, target: Type[M], config: dict):
        self.target = target
        self.config = config

    def __getattr__(self, item):
        if item in self.config:
            return self.config.get(item)
        raise AttributeError(item)

    def handle(self, **kwargs):
        message = self._transform_input(**kwargs)
        if isinstance(message, ffd.Command):
            ret = self.invoke(message)
        elif isinstance(message, ffd.Query):
            ret = self.query(message)
        elif isinstance(message, ffd.Event):
            return self.dispatch(message)
        else:
            raise RuntimeError('Invalid message type')

        return self._transform_output(ret)

    def get_parameters(self):
        return self.target.get_parameters()

    @abstractmethod
    def _transform_input(self, **kwargs) -> ffd.Message:
        pass

    @abstractmethod
    def _transform_output(self, message: ffd.Message):
        pass
