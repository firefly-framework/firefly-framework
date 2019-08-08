from __future__ import annotations

from dataclasses import dataclass

import firefly as ff


@dataclass
class User(ff.AggregateRoot):
    id: str = ff.id()
    name: str = ff.required()
    email: str = ff.required()
