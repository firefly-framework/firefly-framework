from __future__ import annotations

from typing import List

import firefly.domain as ffd

from ..aggregate_root import AggregateRoot
from ..entity import id_, list_


class NetworkTopology(AggregateRoot):
    id: str = id_()
    forwarders: List[ffd.Forwarder] = list_()
