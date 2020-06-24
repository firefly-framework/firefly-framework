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


class RegisterMiddleware:
    def __call__(self, index: int = None, buses: List[str] = None, cb: Callable = None, replace: type = None):
        """
        Decorator to mark a class for insertion into the middleware stack in at least one of the buses.

        :param index: Optional positional index at which to insert the middleware.
        :param buses: Optional list of buses to which to add this middleware. Can contain 'event', 'command' and/or
        'query'
        :param cb: Optional callback that takes the bus type and the current list of middleware and returns a numeric
        index at which to insert the middleware.
        :param replace: Optional class type. If provided, the first matching middleware in the bus will be replaced.
        :return:
        """
        def middleware_wrapper(cls):
            try:
                cls.set_middleware_config({
                    'index': index,
                    'buses': buses,
                    'cb': cb,
                    'replace': replace,
                })
            except AttributeError:
                raise error.FrameworkError('@middleware used on invalid target')
            return cls

        return middleware_wrapper


register_middleware = RegisterMiddleware()
