from __future__ import annotations

from dataclasses import fields
from typing import TypeVar, Generic, Optional, Union

import firefly.domain as ffd

from .crud_operation import CrudOperation

T = TypeVar('T')


class GetEntity(Generic[T], ffd.Service, ffd.GenericBase, CrudOperation, ffd.SystemBusAware):
    _registry: ffd.Registry = None

    def __call__(self, **kwargs) -> Optional[Union[ffd.Message, object]]:
        type_ = self._type()

        ret = self._registry(type_).find(kwargs[self._find_pk(type_)])
        self.dispatch(self._build_event(type_, 'get'))
        return ret

    @staticmethod
    def _find_pk(type_):
        for field_ in fields(type_):
            if 'pk' in field_.metadata:
                return field_.name
