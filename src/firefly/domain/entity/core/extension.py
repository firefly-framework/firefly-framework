from __future__ import annotations

import firefly_di as di
from firefly.domain.entity import Entity

from ..entity import required, hidden


class Extension(Entity):
    name: str = required()
    config: dict = required()
    container: di.Container = hidden()

    def __post_init__(self):
        self.entities = []
        self.command_handlers = []
        self.query_handlers = []
        self.event_listeners = []
