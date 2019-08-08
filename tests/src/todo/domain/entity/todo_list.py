from __future__ import annotations

from dataclasses import dataclass
from typing import List

import firefly as ff

from .task import Task
from .user import User


@ff.on('iam.UserCreated', action='create')
@dataclass
class TodoList(ff.AggregateRoot):
    id: str = ff.id()
    user: User = ff.required()
    name: str = ff.optional()
    tasks: List[Task] = ff.list_()

    def __post_init__(self):
        if self.name is None:
            self.name = f"{self.user.name}'s TODO List"

    def add_task(self, name: str):
        t = Task(name=name)
        self.tasks.append(t)
        self.dispatch('TaskAdded', t)

    def remove_task(self, task: Task):
        self.tasks.remove(task)

    def complete_task(self, task: Task):
        pass
