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
from typing import TypeVar, Generic, Optional, Union

import firefly.domain as ffd

from .crud_operation import CrudOperation
from ..core.application_service import ApplicationService
from ..messaging.system_bus import SystemBusAware
from ...value_object.generic_base import GenericBase

T = TypeVar('T')


class UpdateEntity(Generic[T], ApplicationService, GenericBase, CrudOperation, SystemBusAware):
    _registry: ffd.Registry = None

    def __call__(self, **kwargs) -> bool:
        type_ = self._type()
        id_arg = type_.match_id_from_argument_list(kwargs)
        entity = self._registry(type_).find(list(id_arg.values()).pop())
        entity.load_dict(kwargs)
        self.dispatch(self._build_event(type_, 'update', asdict(entity), entity.get_class_context()))

        return True
