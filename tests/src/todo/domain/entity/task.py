from __future__ import annotations

from dataclasses import dataclass

import firefly as ff


@dataclass
class Task(ff.Entity):
    id: str = ff.id()
    name: str = ff.required()
    complete: bool = ff.optional(default=False)

    def complete_task(self):
        self.complete = True
