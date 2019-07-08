from __future__ import annotations

from dataclasses import fields
from typing import TypeVar, Generic, Optional, Union

import firefly.domain as ffd

from .crud_operation import CrudOperation

T = TypeVar('T')


class CreateEntity(Generic[T], ffd.Service, ffd.GenericBase, CrudOperation):
    _registry: ffd.Registry = None
    _bus: ffd.MessageBus = None

    def __call__(self, **kwargs) -> Optional[Union[ffd.Message, object]]:
        type_ = self._type()
        entity = type_(**self._get_constructor_args(type_, kwargs))
        self._registry(type_).add(entity).commit()
        self._bus.dispatch(self._build_event(type_, 'create'))

        return entity

    @staticmethod
    def _get_constructor_args(type_, kwargs):
        args = {}
        for field_ in fields(type_):
            if field_.name in kwargs:
                args[field_.name] = kwargs[field_.name]

        return args
