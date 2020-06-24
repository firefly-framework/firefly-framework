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

from typing import List, Union, Callable

# __pragma__('skip')
from abc import ABC
# __pragma__('noskip')
# __pragma__ ('ecom')
"""?
from firefly.presentation.web.polyfills import ABC
?"""
# __pragma__ ('noecom')
# __pragma__('opov')

from firefly.domain.service.messaging.middleware_stack import MiddlewareStack
import firefly.domain as ffd


class MessageBus:
    _middleware: list = []
    _handle: MiddlewareStack = None

    def __init__(self, middleware: List[Union[ffd.Middleware, Callable]]):
        self._middleware = middleware
        self._handle = MiddlewareStack(self._middleware)

    @property
    def middleware(self):
        return self._handle.middleware

    @middleware.setter
    def middleware(self, value):
        self._handle.middleware = value

    def add(self, item: Union[ffd.Middleware, Callable]):
        self._handle.add(item)
        
    def insert(self, index: int, item: Union[ffd.Middleware, Callable]):
        self._handle.insert(index, item)

    def replace(self, which: type, with_: ffd.Middleware):
        return self._handle.replace(which, with_)

    def dispatch(self, message: ffd.Message):
        return self._handle(message)


class MessageBusAware(ABC):
    _bus: MessageBus = None

    def dispatch(self, message: ffd.Message):
        return self._bus.dispatch(message)
