from __future__ import annotations

from .message import Message


class Command(Message):
    def __init__(self, **kwargs):
        body = None
        if 'body' in kwargs:
            body = kwargs['body']
            del kwargs['body']
        super().__init__(body=body, headers=kwargs)
