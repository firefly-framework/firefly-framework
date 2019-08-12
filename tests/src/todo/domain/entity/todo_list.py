from __future__ import annotations

from dataclasses import dataclass, asdict
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

    def add_task(self, task: Task):
        self.tasks.append(task)
        self.dispatch('TaskAdded', asdict(task))

    def remove_task(self, task: Task):
        self.tasks.remove(task)

    def complete_task(self, task_id: str):
        for task in self.tasks:
            if task_id == task.id:
                task.complete_task()
                self.dispatch('TaskCompleted', asdict(task))
                return
        raise Exception(f'Task {task_id} not found in TodoList {self}')
