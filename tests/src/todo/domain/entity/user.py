from __future__ import annotations

import firefly as ff


@ff.entity
class User:
    id: str = ff.id_()
    name: str = ff.required()
