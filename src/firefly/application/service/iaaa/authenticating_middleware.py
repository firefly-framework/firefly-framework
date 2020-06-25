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

from typing import Callable

import firefly.domain as ffd


class AuthenticatingMiddleware(ffd.Middleware, ffd.ChainOfResponsibility):
    def __call__(self, message: ffd.Message, next_: Callable) -> ffd.Message:
        self.handle(message)
        return next_(message)

    def handle(self, message: ffd.Message):
        if len(self._handlers) == 0:
            return True

        success = False
        for handler in self._handlers:
            try:
                if handler.handle(message) is True:
                    success = True
                    break
            except ffd.UnauthenticatedError:
                pass

        if not success:
            raise ffd.UnauthenticatedError()
