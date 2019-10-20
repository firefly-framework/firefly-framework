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
from typing import List, Union, Type

import firefly.domain as ffd

from ..messaging.system_bus import SystemBusAware
from ..logging.logger import LoggerAware
from ...utils import FireflyType


class ApplicationService(FireflyType, ABC, SystemBusAware, LoggerAware):
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
    def has_handlers(cls):
        return cls.has_listeners() or cls.has_command_handlers() or cls.has_query_handlers()

    @classmethod
    def locate_message(cls, message: Union[str, Type[ffd.Message]]):
        if cls.has_listeners():
            for event_listener in cls.get_listeners():
                if message == event_listener['event']:
                    return event_listener, 'event'
        if cls.has_command_handlers():
            for command_handler in cls.get_command_handlers():
                if message == command_handler['command']:
                    return command_handler, 'command'
        if cls.has_query_handlers():
            for query_handler in cls.get_query_handlers():
                if message == query_handler['query']:
                    return query_handler, 'query'

    @classmethod
    def has_listeners(cls):
        return cls.get_listeners() is not None

    @classmethod
    def has_command_handlers(cls):
        return cls.get_command_handlers() is not None

    @classmethod
    def has_query_handlers(cls):
        return cls.get_query_handlers() is not None

    @classmethod
    def get_listeners(cls):
        try:
            return getattr(cls, '__ff_listener')
        except AttributeError:
            pass

    @classmethod
    def get_command_handlers(cls):
        try:
            return getattr(cls, '__ff_command_handler')
        except AttributeError:
            pass

    @classmethod
    def get_query_handlers(cls):
        try:
            return getattr(cls, '__ff_query_handler')
        except AttributeError:
            pass

    @classmethod
    def add_listener(cls, events: Union[ffd.Event, List[ffd.Event]]):
        cls._set_or_append('__ff_event_listener', events)

    @classmethod
    def add_command_handler(cls, commands: Union[ffd.Command, List[ffd.Command]]):
        cls._set_or_append('__ff_command_handler', commands)

    @classmethod
    def add_query_handler(cls, query: Union[ffd.Query, List[ffd.Query]]):
        cls._set_or_append('__ff_query_handler', query)

    @classmethod
    def _set_or_append(cls, key: str, items: Union[ffd.Message, List[ffd.Message]]):
        if not isinstance(items, list):
            items = [items]

        if hasattr(cls, key):
            setattr(cls, key, getattr(cls, key).extend(items))
        else:
            setattr(cls, key, items)
