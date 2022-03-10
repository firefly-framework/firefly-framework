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

from typing import TypeVar, Generic, Optional, Union

import firefly.domain as ffd

from .crud_operation import CrudOperation
from ..core.application_service import ApplicationService
from ..messaging.system_bus import SystemBusAware
from ...value_object.generic_base import GenericBase

T = TypeVar('T')


class ReadEntity(Generic[T], ApplicationService, GenericBase, CrudOperation, SystemBusAware):
    """
    DEPRECATED. I don't think this is actually used. See query_service.py instead.
    """
    _registry: ffd.Registry = None

    def __call__(self, **kwargs) -> Optional[Union[ffd.Message, object]]:
        print(kwargs)
        type_ = self._type()
        id_arg = type_.match_id_from_argument_list(kwargs)
        if id_arg:
            ret = self._registry(type_).find(list(id_arg.values()).pop())
            return ret

        limit = None
        offset = None
        if 'limit' in kwargs and 'offset' in kwargs:
            print('paginated!!')
            limit = kwargs.get('limit')
            offset = kwargs.get('offset')

        entities = self._registry(type_)

        if 'criteria' in kwargs:
            print('we have criteria')
            criteria = ffd.BinaryOp.from_dict(kwargs.get('criteria'))
            entities = self._registry(type_).filter(criteria)

        paginated = False
        count = None
        if limit is not None and offset is not None:
            print('paginating response')
            count = len(entities)
            entities = entities[offset:(offset + limit)]
            paginated = True

        if 'sort' in kwargs:
            print('sorting response')
            entities = entities.sort(lambda: kwargs.get('sort'))

        if paginated:
            print('returning an envelope')
            return ffd.Envelope.wrap(list(entities)).set_range(
                offset, limit, count - 1
            )

        print('returning normal')
        return list(entities)
