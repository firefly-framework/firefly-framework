from __future__ import annotations

from dataclasses import dataclass

import firefly as ff


@dataclass
class User(ff.Entity):
    id: str = ff.id()
    name: str = ff.required()
