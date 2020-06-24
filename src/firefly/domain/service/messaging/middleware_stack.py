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

from typing import List, Callable

from firefly.domain.service.messaging.middleware import Middleware
import firefly.domain as ffd

# __pragma__('kwargs')
# __pragma__('opov')


class MiddlewareStack:
    def __init__(self, middleware: List[Middleware]):
        self._middleware = middleware

    @property
    def middleware(self):
        return self._middleware

    @middleware.setter
    def middleware(self, value: List[Middleware]):
        self._middleware = value

    def add(self, item: Middleware):
        self._middleware.append(item)

    def insert(self, index: int, item: Middleware):
        self._middleware.insert(index, item)

    def replace(self, which: type, with_: ffd.Middleware):
        for i, mw in enumerate(self.middleware):
            if mw.__class__ is which:
                self.middleware[i] = with_
                return True
        return False

    def __call__(self, msg: ffd.Message):
        def cb(message, *args, **kwargs):
            return message

        for m in reversed(self._middleware):
            cb = self._nest(cb, m)

        return cb(msg)

    @staticmethod
    def _nest(cb: Callable, middleware: Middleware):
        def callback(message, next_=None):
            return middleware(message, next_=cb)

        return callback
