from __future__ import annotations

import importlib
from dataclasses import fields, asdict
from pydoc import locate
from typing import TypeVar, Generic, Optional, Union

import firefly.domain as ffd

from .crud_operation import CrudOperation

T = TypeVar('T')


class CreateEntity(Generic[T], ffd.Service, ffd.GenericBase, CrudOperation, ffd.SystemBusAware):
    _registry: ffd.Registry = None

    def __call__(self, **kwargs) -> Optional[Union[ffd.Message, object]]:
        type_ = self._type()
        entity = type_(**ffd.build_argument_list(kwargs, type_))
        self._registry(type_).add(entity)
        self.dispatch(self._build_event(kwargs['message'], type_, 'create', kwargs['message'].source_context))

        return entity

    @staticmethod
    def _get_constructor_args(type_, kwargs):
        args = {}
        for field_ in fields(type_):
            if field_.name in kwargs:
                args[field_.name] = kwargs[field_.name]

        return args
