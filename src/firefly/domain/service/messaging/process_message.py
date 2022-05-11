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


class ProcessMessage:
    _kernel: ffd.Kernel = None

    def __call__(self, message: ffd.Message):
        app_service = None
        print(str(message))
        return
        if isinstance(message, ffd.Command) and str(message) in self._kernel.get_command_handlers():
            app_service = self._kernel.get_command_handlers()[str(message)]
        elif isinstance(message, ffd.Query) and str(message) in self._kernel.get_query_handlers():
            app_service = self._kernel.get_query_handlers()[str(message)]
        elif isinstance(message, ffd.Event) and str(message) in self._kernel.get_event_listeners():
            return list(map(
                lambda s: s(**ffd.build_argument_list(message.to_dict(), s)),
                self._kernel.get_event_listeners()[str(message)]
            ))

        if app_service is None:
            raise ffd.ConfigurationError()

        return app_service(**ffd.build_argument_list(message.to_dict(), app_service))
