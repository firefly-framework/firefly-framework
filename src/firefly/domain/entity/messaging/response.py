from __future__ import annotations

import firefly.domain as ffd

from .message import Message


class Response(Message):
    pass


def response(_cls=None, **kwargs):
    return ffd.generate_dc(Response, _cls, **kwargs)
