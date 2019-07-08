from __future__ import annotations

from abc import ABC
from typing import List, Union

import firefly.domain as ffd


class Port(ABC):
    id: str = None
    app_id: str = None
    service: Union[ffd.Service, str] = None
    service_instance: ffd.Service = None
    target: object = None
    parent: Port = None
    children: List[Port] = []

    def __init__(self, id_: str, target: object, service: Union[ffd.Service, str] = None, parent: Port = None,
                 app_id: str = None):
        self.id = id_
        self.app_id = app_id
        self.target = target
        self.service = service
        self.parent = parent

    def extend(self, port: Port):
        self.parent = port
        port.children.append(self)
