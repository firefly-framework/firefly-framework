from __future__ import annotations

from dataclasses import dataclass, MISSING
from typing import Any


@dataclass
class Parameter:
    name: str = MISSING
    type: Any = MISSING
    default: Any = MISSING
