from __future__ import annotations

import firefly as ff

import tests.src.calendar.domain as cal


class Reminder(ff.Entity):
    id: str = ff.id_()
    event: cal.Event = ff.required()
