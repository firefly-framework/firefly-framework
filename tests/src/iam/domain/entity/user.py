from __future__ import annotations

import firefly as ff


class User(ff.AggregateRoot):
    id: str = ff.id_()
    name: str = ff.required()
    email: str = ff.required()
