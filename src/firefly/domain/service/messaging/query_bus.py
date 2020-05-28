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

from typing import Union, Callable

# __pragma__('skip')
from abc import ABC
# __pragma__('noskip')
# __pragma__ ('ecom')
"""?
from firefly.presentation.web.polyfills import ABC
?"""
# __pragma__ ('noecom')

import firefly.domain as ffd

from firefly.domain.service.messaging.message_bus import MessageBus


class QueryBus(MessageBus):
    _message_factory: ffd.MessageFactory = None

    # __pragma__ ('kwargs')
    def request(self, request: Union[ffd.Query, str], criteria: Union[ffd.BinaryOp, Callable] = None,
                data: dict = None):
        if criteria is not None and not isinstance(criteria, ffd.BinaryOp):
            criteria = criteria(ffd.EntityAttributeSpy())
        if isinstance(request, str):
            request = self._message_factory.query(request, criteria, data or {})
        return self.dispatch(request)
    # __pragma__ ('nokwargs')


class QueryBusAware(ABC):
    _query_bus: QueryBus = None

    # __pragma__ ('kwargs')
    def request(self, request: Union[ffd.Query, str], criteria: Union[ffd.BinaryOp, Callable] = None,
                data: dict = None):
        return self._query_bus.request(request, criteria, data)
    # __pragma__ ('nokwargs')
