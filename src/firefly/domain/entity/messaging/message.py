from __future__ import annotations

import uuid
from dataclasses import dataclass, field, asdict

import firefly.domain as ffd
from ..entity import dict_, optional


@dataclass(eq=False, repr=False)
class Message:
    headers: dict = dict_()
    source_context: str = optional()
    _id: str = None

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
