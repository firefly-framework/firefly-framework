from __future__ import annotations

from typing import TypeVar, Type, Tuple, Union

import firefly.domain as ffd

from .repository import Repository
from ..entity.entity import Entity

E = TypeVar('E', bound=Entity)


class Registry:
    def __init__(self):
        self._factories = {}
        self._default_factory = None

    def __call__(self, entity: Type[E]) -> Repository:
        for k, v in self._factories.items():
            if issubclass(entity, k):
                return v(entity)

        if self._default_factory is not None:
            return self._default_factory(entity)

        raise ffd.FrameworkError(
            'No registry found for entity {}. Have you installed a persistence extension, '
            'like firefly_sqlalchemy? If so, you may have a configuration issue.'.format(entity)
        )

    def register_factory(self, types: Union[Type[E], Tuple[Type[E]]], factory: ffd.RepositoryFactory):
        self._factories[types] = factory

    def set_default_factory(self, factory: ffd.RepositoryFactory):
        self._default_factory = factory
