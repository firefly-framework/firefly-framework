from __future__ import annotations

from dataclasses import dataclass
from typing import List

import firefly as ff

import tests.src.calendar.domain as cal


@dataclass
class Event(ff.Entity):
    id: str = ff.id()
    name: str = ff.required()
    reminders: List[cal.Reminder] = ff.list_()
