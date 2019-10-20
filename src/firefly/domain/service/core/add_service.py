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

import firefly.domain as ffd
import firefly_di as di

from .application_service import ApplicationService


class AddApplicationService(ApplicationService):
    _container: di.Container = None
    _event_resolver: ffd.EventResolvingMiddleware = None
    _command_resolver = ffd.CommandResolvingMiddleware = None
    _query_resolver = ffd.QueryResolvingMiddleware = None

    def __call__(self, fqn: str, args: dict = None):
        args = args or {}
        cls = ffd.load_class(fqn)
        for key in ('__ff_command_handler', '__ff_listener', '__ff_query_handler'):
            if hasattr(cls, key):
                mw = ffd.ServiceExecutingMiddleware(self._container.build(cls, **args))
                setattr(mw, key, getattr(cls, key))
                self._add_middleware(mw)
