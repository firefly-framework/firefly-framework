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

from abc import ABC, abstractmethod
from typing import Any

from ...entity.messaging.event import Event
from ...entity.messaging.command import Command
from ...entity.messaging.query import Query


class MessageTransport(ABC):
    """
    Pass messages between services.
    """
    @abstractmethod
    def dispatch(self, event: Event) -> None:
        pass

    @abstractmethod
    def invoke(self, command: Command) -> Any:
        pass

    @abstractmethod
    def request(self, query: Query) -> Any:
        pass
