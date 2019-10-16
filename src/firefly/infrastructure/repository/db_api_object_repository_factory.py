from __future__ import annotations

from typing import Type

import firefly.domain as ffd
from firefly import Repository
from firefly.domain.repository.repository_factory import E


class DbApiObjectRepositoryFactory(ffd.RepositoryFactory):
    def __call__(self, entity: Type[E]) -> Repository:
        pass
