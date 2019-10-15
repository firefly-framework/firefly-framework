from __future__ import annotations

from typing import TypeVar, Type, Tuple, Union

import firefly.domain as ffd

from .repository import Repository
from ..entity.aggregate_root import AggregateRoot

AR = TypeVar('AR', bound=AggregateRoot)


class Registry:
    def __init__(self):
        self._cache = {}
        self._factories = {}
        self._default_factory = None

    def __call__(self, entity) -> Repository:
        if not issubclass(entity, ffd.AggregateRoot):
            raise ffd.LogicError('Repositories can only be generated for aggregate roots')

        if entity not in self._cache:
            for k, v in self._factories.items():
                if issubclass(entity, k):
                    self._cache[entity] = v(entity)

            if self._default_factory is not None:
                self._cache[entity] = self._default_factory(entity)

            if entity not in self._cache:
                raise ffd.FrameworkError(
                    'No registry found for entity {}. Have you configured a persistence mechanism or extension, '
                    'like MemoryRepository or firefly_sqlalchemy?'.format(entity)
                )

        return self._cache[entity]

    def register_factory(self, types: Union[Type[AR], Tuple[Type[AR]]], factory: ffd.RepositoryFactory):
        self._factories[types] = factory

    def set_default_factory(self, factory: ffd.RepositoryFactory):
        self._default_factory = factory

    def clear_cache(self):
        self._cache = {}
