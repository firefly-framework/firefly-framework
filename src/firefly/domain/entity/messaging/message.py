from __future__ import annotations

import uuid
from abc import ABC

import firefly.domain as ffd

from ..entity import dict_, optional
from ...utils import MessageMeta


class Message(metaclass=MessageMeta):
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

    def __str__(self):
        return f'{self.source_context}.{self.__class__.__name__}' \
            if self.source_context is not None else self.__class__.__name__

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        if isinstance(other, str) and other == str(self):
            return True
        try:
            return isinstance(self, other)
        except TypeError:
            return False
