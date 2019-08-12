from __future__ import annotations

from typing import TypeVar, Generic

import firefly.domain as ffd
import inflection

T = TypeVar('T', bound=ffd.AggregateRoot)


class InvokeCommand(Generic[T], ffd.GenericBase, ffd.Service):
    _registry: ffd.Registry = None

    def __init__(self, method: str):
        self._method = method

    def __call__(self, **kwargs):
        try:
            aggregate = self._registry(self._type()).find(kwargs[self._aggregate_name_snake()])
        except KeyError:
            raise ffd.MissingArgument(self._aggregate_name_snake())

        method = getattr(aggregate, self._method)
        return method(**ffd.build_argument_list(kwargs, method))

    def _aggregate_name_snake(self):
        return inflection.underscore(self._type().__name__)
