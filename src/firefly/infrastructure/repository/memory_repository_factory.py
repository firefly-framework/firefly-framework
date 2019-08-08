from __future__ import annotations

from typing import Type

import firefly.domain as ffd
from firefly import Repository
from firefly.domain.repository.repository_factory import E

from .memory_repository import MemoryRepository


class MemoryRepositoryFactory(ffd.RepositoryFactory):
    def __call__(self, entity: Type[E]) -> Repository:
        class Repo(MemoryRepository[entity]):
            pass

        return Repo()
