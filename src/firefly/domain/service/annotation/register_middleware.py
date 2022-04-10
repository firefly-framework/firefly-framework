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

from firefly.domain import error
import firefly.domain.constants as const


class RegisterMiddleware:
    def __call__(self, **kwargs):
        """
        Decorator to mark a class for insertion into the middleware stack in at least one of the buses.
        """
        def middleware_wrapper(cls):
            try:
                setattr(cls, const.MIDDLEWARE, kwargs)
            except AttributeError:
                raise error.FrameworkError('@middleware used on invalid target')
            return cls

        return middleware_wrapper


middleware = RegisterMiddleware()
