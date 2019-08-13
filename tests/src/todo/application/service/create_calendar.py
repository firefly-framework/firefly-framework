from __future__ import annotations

import firefly as ff


@ff.on('todo.TodoListCreated')
class CreateCalendar(ff.Service):
    def __call__(self, id_: str):
        self.invoke('calendar.CreateCalendar', {'id': id_})
