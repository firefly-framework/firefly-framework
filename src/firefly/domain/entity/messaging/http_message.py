from __future__ import annotations

from dataclasses import dataclass, MISSING

from .message import Message


@dataclass
class HttpMessage(Message):
    http_headers: dict = MISSING
    body: str = MISSING
