from __future__ import annotations

from typing import Generic, TypeVar

import firefly.domain as ffd

from .application_service import ApplicationService
from ...value_object.generic_base import GenericBase

T = TypeVar('T')


class QueryService(Generic[T], GenericBase, ApplicationService):
    _registry: ffd.Registry = None

    def __call__(self, **kwargs):
        try:
            if 'criteria' in kwargs:
                return self._registry(self._type()).find_all_matching(ffd.BinaryOp.from_dict(kwargs['criteria']))
            else:
                return self._registry(self._type()).all()
        except KeyError:
            raise ffd.MissingArgument(self._type().id_name())
