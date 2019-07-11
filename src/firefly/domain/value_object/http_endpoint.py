from __future__ import annotations

from dataclasses import dataclass, MISSING


@dataclass
class HttpEndpoint:
    method: str = MISSING
    path: str = MISSING
