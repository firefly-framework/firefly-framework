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

import inspect

import firefly as ff
import firefly.domain.error as error
from firefly.domain.entity.core.http_endpoint import HttpEndpoint


class Rest:
    def __call__(self, route: str, method: str = 'GET', generates: ff.TypeOfMessage = None, gateway: str = None,
                 query_params: dict = None):
        def on_wrapper(cls):
            endpoint = HttpEndpoint(
                route=route,
                method=method,
                message=generates,
                gateway=gateway,
                query_params=query_params
            )

            try:
                cls.add_endpoint(endpoint)
            except AttributeError:
                if inspect.isfunction(cls):
                    ff.add_endpoint(cls, endpoint)
                else:
                    raise error.FrameworkError('@rest used on invalid target')
            return cls

        return on_wrapper


rest = Rest()
