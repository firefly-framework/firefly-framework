from __future__ import annotations

import uuid
from dataclasses import asdict, fields

import firefly.domain as ffd

from ..entity import dict_
from ...utils import FireflyType
from ...utils import MessageMeta


class Message(FireflyType, metaclass=MessageMeta):
    headers: dict = dict_()
    _id: str = None
    _context: str = None

    def __init__(self, **kwargs):
        raise TypeError('Message is an abstract base class')

    def get_parameters(self):
        return ffd.get_arguments(self.__init__)

    def __post_init__(self):
        if self._id is None:
            self._id = str(uuid.uuid1())
        if self._context is None:
            self._context = self.__module__.split('.')[0]

    # noinspection PyDataclass
    def to_dict(self, recursive: bool = True) -> dict:
        if recursive:
            return asdict(self)

        ret = {}
        for field_ in fields(self):
            ret[field_.name] = getattr(self, field_.name)

        return ret
