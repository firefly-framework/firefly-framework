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
import firefly_di as di

from .authorize_scope import AuthorizeScope


class AuthorizingMiddleware(ffd.Middleware, ffd.ChainOfResponsibility):
    _container: di.Container = None

    def __init__(self):
        super().__init__()
        self._handlers.append(self._container.build(AuthorizeScope))

    def __call__(self, message: ffd.Message, next_: Callable) -> ffd.Message:
        if self.handle(message) is not True:
            raise ffd.UnauthorizedError()
        return next_(message)
