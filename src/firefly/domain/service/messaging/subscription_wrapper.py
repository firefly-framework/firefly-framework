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

from typing import Callable, TypeVar, Type

import firefly.domain as ffd

from firefly.domain.service.messaging.middleware import Middleware
from firefly.domain.entity.messaging.message import Message

M = TypeVar('M', bound=Message)


class SubscriptionWrapper(Middleware):
    def __init__(self, middleware: ffd.Middleware, type_: Type[M]):
        self._middleware = middleware
        self._type = type_

    def __call__(self, message: ffd.Message, next_: Callable) -> ffd.Message:
        if (isinstance(self._type, str) and message == self._type) or (
                not isinstance(self._type, str) and isinstance(message, self._type)):
            return self._middleware(message, next_)
        else:
            return next_(message)

    def __repr__(self):
        return '<SubscriptionWrapper {}, {}>'.format(repr(self._middleware), repr(self._type))
