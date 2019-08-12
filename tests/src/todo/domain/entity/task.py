from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

import firefly as ff


@dataclass
class Task(ff.Entity):
    id: str = ff.id()
    name: str = ff.required()
    due_date: datetime = ff.required()
    complete: bool = ff.optional(default=False)

    def complete_task(self):
        self.complete = True

    def is_overdue(self):
        return datetime.now() >= self.due_date
