from __future__ import annotations

from dataclasses import asdict
from typing import List

import firefly as ff

import tests.src.calendar.domain as cal


class Calendar(ff.AggregateRoot):
    id: str = ff.id_()
    events: List[cal.Event] = ff.list_()

    def add_event(self, event: cal.Event):
        self.events.append(event)
        self.dispatch('EventAdded', asdict(event))

    def add_reminder(self, event_id: str, reminder: cal.Reminder):
        for event in self.events:
            if event.id == event_id:
                event.reminders.append(reminder)
                self.dispatch('ReminderAdded', asdict(reminder))
