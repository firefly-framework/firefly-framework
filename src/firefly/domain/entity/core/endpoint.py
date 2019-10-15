from __future__ import annotations

from ..entity import Entity, required, optional


class Endpoint(Entity):
    route: str = required()
    method: str = optional(default='GET')
    target: str = optional()
