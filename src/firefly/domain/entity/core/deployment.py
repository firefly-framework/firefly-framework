from __future__ import annotations

from typing import List

import firefly.domain as ffd
from ..aggregate_root import AggregateRoot
from ..entity import list_, required


class Deployment(AggregateRoot):
    environment: str = required()
    provider: str = required()
    api_gateways: List[ffd.ApiGateway] = list_()
    network_topology: ffd.NetworkTopology = None
