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

    def __post_init__(self):
        self.ports = []
        self.queue = ffd.Queue(name=f'{inflection.camelize(self.name)}Queue', subscribers=[self])
