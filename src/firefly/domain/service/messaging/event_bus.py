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


class EventBus(MessageBus):
    _message_factory: ffd.MessageFactory = None

    def dispatch(self, event: Union[ffd.Event, str], data: dict = None):
        if isinstance(event, str) and data is not None:
            event = self._message_factory.event(event, data)
        return super().dispatch(event)


class EventBusAware(ABC):
    _event_bus: EventBus = None

    def dispatch(self, event: Union[ffd.Event, str], data: dict = None):
        return self._event_bus.dispatch(event, data)
