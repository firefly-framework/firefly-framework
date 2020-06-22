#  Copyright (c) 2019 JD Williams
#
#  This file is part of Firefly, a Python SOA framework built by JD Williams. Firefly is free software; you can
#  redistribute it and/or modify it under the terms of the GNU General Public License as published by the
#  Free Software Foundation; either version 3 of the License, or (at your option) any later version.
#
#  Firefly is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the
#  implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
#  Public License for more details. You should have received a copy of the GNU Lesser General Public
#  License along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#  You should have received a copy of the GNU General Public License along with Firefly. If not, see
#  <http://www.gnu.org/licenses/>.

from __future__ import annotations

from dataclasses import asdict
from typing import List

import firefly as ff

import firefly_test.calendar.domain as cal


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
