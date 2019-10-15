from __future__ import annotations

from typing import List, Type, Dict

import firefly as ff
import firefly.domain as ffd
import firefly_di as di
import inflection

from ..entity import required, hidden, optional, Entity, id_


class Context(Entity):
    name: str = id_(is_uuid=False)
    config: dict = required()
    container: di.Container = hidden()
    is_extension: bool = optional(default=False)

    def __post_init__(self):
        self.entities = []
        self.ports = []
        self.command_handlers: Dict[Type[ffd.ApplicationService], ff.TypeOfCommand] = {}
        self.query_handlers: Dict[Type[ffd.ApplicationService], ff.TypeOfQuery] = {}
        self.event_listeners: Dict[Type[ffd.ApplicationService], List[ff.TypeOfEvent]] = {}
        self.queue = ffd.Queue(name=f'{inflection.camelize(self.name)}Queue', subscribers=[self])
