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

from typing import Generic, TypeVar

import firefly.domain as ffd

from .application_service import ApplicationService
from ...value_object.generic_base import GenericBase

T = TypeVar('T')


class QueryService(Generic[T], GenericBase, ApplicationService):
    _registry: ffd.Registry = None
    _serializer: ffd.Serializer = None
    _context: str = None

    def __call__(self, **kwargs):
        try:
            if self._type().id_name() in kwargs:
                return self._registry(self._type()).find(kwargs[self._type().id_name()])
        except KeyError:
            raise ffd.MissingArgument(self._type().id_name())

        limit = None
        offset = None
        if 'limit' in kwargs and 'offset' in kwargs:
            limit = int(kwargs.get('limit'))
            offset = int(kwargs.get('offset'))

        entities = self._registry(self._type())

        if 'criteria' in kwargs:
            criteria = kwargs.get('criteria')
            if isinstance(criteria, str):
                criteria = self._serializer.deserialize(criteria)
            criteria = ffd.BinaryOp.from_dict(criteria)
            if '__include_deleted' not in kwargs and hasattr(self._type(), 'deleted_on'):
                criteria &= ffd.Attr('deleted_on').is_none()
            entities = self._registry(self._type()).filter(criteria)
        elif '__include_deleted' not in kwargs and hasattr(self._type(), 'deleted_on'):
            criteria = ffd.Attr('deleted_on').is_none()
            entities = self._registry(self._type()).filter(criteria)

        paginated = False
        count = None
        if limit is not None and offset is not None:
            count = len(entities)
            entities = entities[offset:(offset + limit - 1)]
            paginated = True

        if 'sort' in kwargs:
            entities = entities.sort(lambda x: kwargs.get('sort'))

        if paginated:
            return {
                'offset': offset,
                'limit': limit,
                'count': count,
                'data': list(entities),
            }

        return list(map(lambda e: e.to_dict(force_all=self._kernel.is_admin(self._context)), entities))
