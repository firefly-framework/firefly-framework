from __future__ import annotations

from dataclasses import asdict
from typing import TypeVar, Generic, Optional, Union

import firefly.domain as ffd

from .crud_operation import CrudOperation
from ..core.service import Service
from ..messaging.system_bus import SystemBusAware
from ...value_object.generic_base import GenericBase

T = TypeVar('T')


class CreateEntity(Generic[T], Service, GenericBase, CrudOperation, SystemBusAware):
    _registry: ffd.Registry = None
    _context_map: ffd.ContextMap = None

    def __call__(self, **kwargs) -> Optional[Union[ffd.Message, object]]:
        type_ = self._type()
        entity = type_(**ffd.build_argument_list(kwargs, type_))
        self._registry(type_).add(entity)
        self.dispatch(self._build_event(type_, 'create', asdict(entity), kwargs['source_context']))

        return entity
