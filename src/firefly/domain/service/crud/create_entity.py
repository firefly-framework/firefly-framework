#  Copyright (c) 2019 JD Williams
#
#  This file is part of Firefly, a Python SOA framework built by JD Williams. Firefly is free software; you can
#  redistribute it and/or modify it under the terms of the GNU General Public License as published by the
#  Free Software Foundation; either version 3 of the License, or (at your option) any later version.
#
#  Firefly is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the
#  implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
#  Public License for more details. You should have received a copy of the GNU Lesser General Public
#  License along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#  You should have received a copy of the GNU General Public License along with Firefly. If not, see
#  <http://www.gnu.org/licenses/>.

from __future__ import annotations

from dataclasses import asdict
from typing import TypeVar, Generic, Type

import firefly.domain as ffd

from .crud_operation import CrudOperation
from ..core.application_service import ApplicationService
from ..messaging.system_bus import SystemBusAware
from ...value_object.generic_base import GenericBase

T = TypeVar('T')


class CreateEntity(Generic[T], ApplicationService, GenericBase, CrudOperation, SystemBusAware):
    _registry: ffd.Registry = None
    _context_map: ffd.ContextMap = None

    def __call__(self, **kwargs) -> ffd.Entity:
        type_ = self._type()
        method = self._find_factory_method(type_)
        if method is not None:
            entity = method(type_, **kwargs)
        else:
            try:
                entity = type_(**ffd.build_argument_list(kwargs, type_))
            except ffd.MissingArgument as e:
                raise ffd.MissingArgument(f'In CreateEntity[{self._type()}]: {str(e)}')
        self._registry(type_).append(entity)
        self.dispatch(self._build_event(type_, 'create', entity.to_dict(), entity.get_class_context()))

        return entity

    @staticmethod
    def _find_factory_method(type_: Type[ffd.Entity]):
        for k, v in type_.__dict__.items():
            if k == 'create' and isinstance(v, classmethod):
                return v.__func__
        return None
