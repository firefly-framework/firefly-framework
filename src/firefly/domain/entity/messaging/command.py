from __future__ import annotations

import firefly.domain as ffd

from .message import Message


class Command(Message):
    pass


def command(_cls=None, **kwargs):
    return ffd.generate_dc(Command, _cls, **kwargs)
