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

from abc import ABC
from typing import Union

import firefly.domain as ffd

from .message_bus import MessageBus


class CommandBus(MessageBus):
    _message_factory: ffd.MessageFactory = None

    def invoke(self, command: Union[ffd.Command, str], data: dict = None):
        if isinstance(command, str) and data is not None:
            command = self._message_factory.command(command, data)
        return self.dispatch(command)


class CommandBusAware(ABC):
    _command_bus: CommandBus = None

    def invoke(self, command: Union[ffd.Command, str], data: dict = None):
        return self._command_bus.invoke(command, data)
