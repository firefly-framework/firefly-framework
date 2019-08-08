from __future__ import annotations

from abc import ABC

from .message import Message


class Event(Message, ABC):
    pass
