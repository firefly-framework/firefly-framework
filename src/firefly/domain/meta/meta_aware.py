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
from typing import List, Dict, Type

import firefly as ff


class MetaAware(ABC):
    _events: Dict[Type[MetaAware], List[ff.TypeOfEvent]] = {}
    _command: Dict[Type[MetaAware], ff.TypeOfCommand] = {}
    _query: Dict[Type[MetaAware], ff.TypeOfQuery] = {}
    _endpoints: Dict[Type[MetaAware], List[ff.Endpoint]] = {}

    @classmethod
    def is_handler(cls):
        return cls.is_event_listener() or cls.is_query_handler() or cls.is_command_handler()

    @classmethod
    def add_event(cls, event: ff.TypeOfEvent):
        if cls not in cls._events:
            cls._events[cls] = []
        cls._events[cls].append(event)

    @classmethod
    def add_endpoint(cls, endpoint: ff.Endpoint):
        if cls not in cls._endpoints:
            cls._endpoints[cls] = []
        cls._endpoints[cls].append(endpoint)

    @classmethod
    def set_command(cls, command: ff.TypeOfCommand):
        cls._command[cls] = command

    @classmethod
    def set_query(cls, query: ff.TypeOfQuery):
        cls._query[cls] = query

    @classmethod
    def is_event_listener(cls):
        return cls in cls._events

    @classmethod
    def is_command_handler(cls):
        return cls in cls._command

    @classmethod
    def is_query_handler(cls):
        return cls in cls._query

    @classmethod
    def has_endpoints(cls):
        return cls in cls._endpoints

    @classmethod
    def get_events(cls):
        return cls._events[cls]

    @classmethod
    def get_command(cls):
        return cls._command[cls]

    @classmethod
    def get_query(cls):
        return cls._query[cls]

    @classmethod
    def get_endpoints(cls):
        return cls._endpoints[cls]
