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
from typing import Union, Type

import firefly.domain as ffd
from firefly.domain.meta.firefly_type import FireflyType
from firefly.domain.meta.meta_aware import MetaAware

from ..logging.logger import LoggerAware
from ..messaging.system_bus import SystemBusAware


class ApplicationService(FireflyType, MetaAware, ABC, SystemBusAware, LoggerAware):
    _event_buffer: ffd.EventBuffer = None

    @abstractmethod
    def __call__(self, **kwargs):
        pass

    def _buffer_events(self, events):
        if isinstance(events, list):
            for event in events:
                if isinstance(event, (ffd.Event, tuple)):
                    self._event_buffer.append(event)
        elif isinstance(events, ffd.Event) or (isinstance(events, tuple) and len(events) == 2):
            self._event_buffer.append(events)

        return events

    @classmethod
    def get_arguments(cls) -> dict:
        return ffd.get_arguments(cls.__call__)

    @classmethod
    def locate_message(cls, message: Union[str, Type[ffd.Message]]):
        if cls.is_event_listener():
            for event in cls.get_events():
                if message == event:
                    return event, 'event'
        if cls.is_command_handler():
            if message == cls.get_command():
                return cls.get_command(), 'command'
        if cls.is_query_handler():
            if message == cls.get_query():
                return cls.get_query(), 'query'
