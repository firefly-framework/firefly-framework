from __future__ import annotations

from abc import ABC

import firefly.domain as ffd

from .message import Message


class Event(Message, ABC):
    pass


def event(_cls=None, **kwargs):
    return ffd.generate_dc(Event, _cls, **kwargs)
