from __future__ import annotations

import firefly as ff


class User(ff.Entity):
    id: str = ff.id_()
    name: str = ff.required()
