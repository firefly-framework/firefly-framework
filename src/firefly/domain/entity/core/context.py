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

from typing import List, Type, Dict

import firefly as ff
import firefly.domain as ffd
import firefly_di as di
import inflection

from ..entity import required, hidden, optional, Entity, id_, dict_, list_


class Context(Entity):
    name: str = id_(is_uuid=False)
    config: dict = required()
    container: di.Container = hidden()
    is_extension: bool = optional(default=False)
    entities: List[Type[Entity]] = list_()
    command_handlers: Dict[Type[ffd.ApplicationService], ff.TypeOfCommand] = dict_()
    query_handlers: Dict[Type[ffd.ApplicationService], ff.TypeOfQuery] = dict_()
    event_listeners: Dict[Type[ffd.ApplicationService], List[ff.TypeOfEvent]] = dict_()
    endpoints: List[ff.Endpoint] = list_()

    def __post_init__(self):
        self.ports = []
        self.queue = ffd.Queue(name=f'{inflection.camelize(self.name)}Queue', subscribers=[self])
