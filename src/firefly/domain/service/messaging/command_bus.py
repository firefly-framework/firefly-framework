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

from typing import Union

# __pragma__('skip')
from abc import ABC
# __pragma__('noskip')
# __pragma__ ('ecom')
"""?
from firefly.presentation.web.polyfills import ABC
?"""
# __pragma__ ('noecom')

import firefly.domain as ffd

from firefly.domain.service.messaging.message_bus import MessageBus


class CommandBus(MessageBus):
    _message_factory: ffd.MessageFactory = None

    def invoke(self, command: Union[ffd.Command, str], data: dict = None, async_: bool = False):
        if isinstance(command, str):
            data = data or {}
            data['_async'] = async_
            command = self._message_factory.command(command, data)
        else:
            setattr(command, '_async', async_)

        return self.dispatch(command)


class CommandBusAware(ABC):
    _command_bus: CommandBus = None

    def invoke(self, command: Union[ffd.Command, str], data: dict = None, async_: bool = False):
        return self._command_bus.invoke(command, data, async_)
