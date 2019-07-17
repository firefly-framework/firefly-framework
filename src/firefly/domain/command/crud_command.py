from __future__ import annotations

from dataclasses import dataclass

from ..entity.messaging.command import Command


@dataclass
class CrudCommand(Command):
    pass
