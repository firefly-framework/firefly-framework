from __future__ import annotations

from typing import List

import firefly.domain as ffd

from ..entity import Entity, list_


class ApiGateway(Entity):
    endpoints: List[ffd.Endpoint] = list_()

    def add(self, endpoint: ffd.Endpoint):
        self.endpoints.append(endpoint)
