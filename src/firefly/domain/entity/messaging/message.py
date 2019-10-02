from __future__ import annotations

import uuid
from dataclasses import asdict

import firefly.domain as ffd

from ..entity import dict_, optional
from ...utils import MessageMeta
from ...utils import FireflyType


class Message(FireflyType, metaclass=MessageMeta):
    headers: dict = dict_()
    source_context: str = optional()
    _id: str = None

    def __init__(self, **kwargs):
        raise TypeError('Message is an abstract base class')

    def get_parameters(self):
        return ffd.get_arguments(self.__init__)

    def __post_init__(self):
        if self._id is None:
            self._id = str(uuid.uuid1())
        if self.source_context is None:
            self.source_context = self.__module__.split('.')[0]

    def to_dict(self) -> dict:
        # noinspection PyDataclass
        return asdict(self)
