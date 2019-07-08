from __future__ import annotations

from dataclasses import fields
from typing import TypeVar, Generic, Optional, Union

import firefly.domain as ffd

from .crud_operation import CrudOperation

T = TypeVar('T')


class DeleteEntity(Generic[T], ffd.Service, ffd.GenericBase, CrudOperation):
    _registry: ffd.Registry = None
    _bus: ffd.MessageBus = None

    def __call__(self, **kwargs) -> Optional[Union[ffd.Message, object]]:
        type_ = self._type()
        entity = self._registry(type_).find(kwargs[self._find_pk(type_)])
        self._registry(type_).remove(entity).commit()
        self._bus.dispatch(self._build_event(type_, 'delete'))

        return

    @staticmethod
    def _find_pk(type_):
        for field_ in fields(type_):
            if 'pk' in field_.metadata:
                return field_.name
