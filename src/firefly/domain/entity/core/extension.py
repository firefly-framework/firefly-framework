from __future__ import annotations

from typing import List, Type, Dict

import firefly as ff
import firefly.domain as ffd
import firefly_di as di
from firefly.domain.entity import Entity

from ..entity import required, hidden


class Extension(Entity):
    name: str = required()
    config: dict = required()
    container: di.Container = hidden()

    def __post_init__(self):
        self.entities = []
        self.ports = []
        self.command_handlers: Dict[Type[ffd.ApplicationService], ff.TypeOfCommand] = {}
        self.query_handlers: Dict[Type[ffd.ApplicationService], ff.TypeOfQuery] = {}
        self.event_listeners: Dict[Type[ffd.ApplicationService], List[ff.TypeOfEvent]] = {}

    def get_services(self):
        return self.command_handlers + self.query_handlers + self.event_listeners
