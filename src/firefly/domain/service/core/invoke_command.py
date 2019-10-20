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

from typing import TypeVar, Generic

import firefly.domain as ffd
import inflection

from ..core.application_service import ApplicationService
from ...entity.aggregate_root import AggregateRoot
from ...value_object.generic_base import GenericBase

T = TypeVar('T', bound=AggregateRoot)


class InvokeCommand(Generic[T], GenericBase, ApplicationService):
    _registry: ffd.Registry = None

    def __init__(self, method: str):
        self._method = method

    def __call__(self, **kwargs):
        try:
            aggregate = self._registry(self._type()).find(kwargs[self._aggregate_name_snake()])
        except KeyError:
            raise ffd.MissingArgument(self._aggregate_name_snake())

        method = getattr(aggregate, self._method)
        return self._buffer_events(
            method(**ffd.build_argument_list(kwargs, method))
        )

    def _aggregate_name_snake(self):
        return inflection.underscore(self._type().__name__)
