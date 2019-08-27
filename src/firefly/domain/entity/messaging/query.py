from __future__ import annotations

import firefly.domain as ffd

from .message import Message


class Query(Message):
    pass


def query(_cls=None, **kwargs):
    return ffd.generate_dc(Query, _cls, **kwargs)
