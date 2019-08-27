from __future__ import annotations

from dataclasses import dataclass

import firefly as ff

import tests.src.calendar.domain as cal


@dataclass
class Reminder(ff.Entity):
    id: str = ff.id_()
    event: cal.Event = ff.required()
