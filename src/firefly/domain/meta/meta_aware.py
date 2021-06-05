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
from typing import List, Dict, Type, Optional

import firefly as ff


class MetaAware(ABC):
    _events: Dict[Type[MetaAware], List[ff.TypeOfEvent]] = {}
    _command: Dict[Type[MetaAware], ff.TypeOfCommand] = {}
    _query: Dict[Type[MetaAware], ff.TypeOfQuery] = {}
    _endpoints: Dict[Type[MetaAware], List[ff.Endpoint]] = {}
    _timers: Dict[Type[MetaAware], ff.Timer] = {}
    _agent: Optional[str] = None
    _agent_extension: Optional[tuple] = None
    _middleware_config: Optional[Dict] = None
    _annotations: Dict[Type[MetaAware], List[ff.ConfigurationAnnotation]] = {}

    @classmethod
    def is_handler(cls):
        return cls.is_event_listener() or cls.is_query_handler() or cls.is_command_handler()

    @classmethod
    def is_middleware(cls):
        return cls._middleware_config is not None

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
    def add_annotation(cls, annotation: ff.ConfigurationAnnotation):
        if cls not in cls._annotations:
            cls._annotations[cls] = []
        cls._annotations[cls].append(annotation)

    @classmethod
    def set_command(cls, command: ff.TypeOfCommand):
        cls._command[cls] = command

    @classmethod
    def set_timer(cls, timer: ff.Timer):
        cls._timers[cls] = timer

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
    def has_timer(cls):
        return cls in cls._timers

    @classmethod
    def is_query_handler(cls):
        return cls in cls._query

    @classmethod
    def has_endpoints(cls):
        return cls in cls._endpoints

    @classmethod
    def has_annotations(cls):
        return cls in cls._annotations

    @classmethod
    def get_events(cls):
        return cls._events[cls]

    @classmethod
    def get_command(cls):
        return cls._command[cls]

    @classmethod
    def get_timer(cls):
        return cls._timers[cls]

    @classmethod
    def get_query(cls):
        return cls._query[cls]

    @classmethod
    def get_endpoints(cls):
        return cls._endpoints[cls]

    @classmethod
    def get_annotations(cls):
        return cls._annotations[cls]

    @classmethod
    def is_agent(cls):
        return cls._agent is not None

    @classmethod
    def set_agent(cls, agent: str):
        cls._agent = agent

    @classmethod
    def get_agent(cls):
        return cls._agent

    @classmethod
    def is_agent_extension(cls):
        return cls._agent_extension is not None

    @classmethod
    def set_agent_extension(cls, agent: str, step: str):
        cls._agent_extension = (agent, step)

    @classmethod
    def get_agent_extension(cls):
        return cls._agent_extension

    @classmethod
    def set_middleware_config(cls, config: dict):
        cls._middleware_config = config

    @classmethod
    def get_middleware_config(cls):
        return cls._middleware_config
