from __future__ import annotations

from dataclasses import fields
from typing import TypeVar, Generic, Optional, Union

import firefly.domain as ffd

from .crud_operation import CrudOperation

T = TypeVar('T')


class UpdateEntity(Generic[T], ffd.Service, ffd.GenericBase, CrudOperation, ffd.SystemBusAware):
    _registry: ffd.Registry = None

    def __call__(self, **kwargs) -> Optional[Union[ffd.Message, object]]:
        type_ = self._type()
        entity = self._registry(type_).find(kwargs[self._find_pk(type_)])
        for k, v in kwargs.items():
            if hasattr(entity, k):
                setattr(entity, k, v)
        self._registry(type_).update(entity).commit()
        self.dispatch(self._build_event(type_, 'update'))

        return entity

    @staticmethod
    def _find_pk(type_):
        for field_ in fields(type_):
            if 'pk' in field_.metadata:
                return field_.name
