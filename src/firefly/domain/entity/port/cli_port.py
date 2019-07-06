from __future__ import annotations

from typing import List

from .port import Port


class CliPort(Port):
    name: str = None
    description: str = None
    alias: dict = None
    help: dict = None
    params: dict = None
    parent: CliPort = None
    children: List[CliPort] = []

    def __init__(self, name: str, target: object, description: str = None, for_: object = None, alias: dict = None,
                 help_: dict = None, params: dict = None, parent: object = None, app_id: str = None):
        self.name = name
        self.description = description
        self.alias = alias
        self.help = help_
        self.params = params or {}
        self.children = []

        super().__init__(id_=f'Cli::{self.app_id}::{name}', target=target, service=for_, parent=parent, app_id=app_id)

    def extend(self, port: CliPort):
        super().extend(port)
        self.params.update(port.params)
