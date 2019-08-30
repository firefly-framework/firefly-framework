from __future__ import annotations

from typing import List

import firefly as ff

import tests.src.calendar.domain as cal


class Event(ff.Entity):
    id: str = ff.id_()
    name: str = ff.required()
    reminders: List[cal.Reminder] = ff.list_()
