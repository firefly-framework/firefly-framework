from __future__ import annotations

from dataclasses import dataclass

from .message import Message
from ..entity import required


@dataclass
class HttpMessage(Message):
    http_headers: dict = required()
    body: str = required()
