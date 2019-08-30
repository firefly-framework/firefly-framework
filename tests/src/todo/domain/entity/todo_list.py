from __future__ import annotations

from typing import List

import firefly as ff

from .task import Task
from .user import User


class TodoList(ff.AggregateRoot, create_on='iam.UserCreated', delete_on='iam.UserDeleted'):
    id: str = ff.id_()
    user: User = ff.required()
    name: str = ff.optional()
    tasks: List[Task] = ff.list_()

    def __post_init__(self):
        if self.name is None:
            self.name = f"{self.user.name}'s TODO List"

    def add_task(self, task: Task) -> ff.EventList:
        self.tasks.append(task)
        return 'TaskAdded', task

    def remove_task(self, task: Task):
        self.tasks.remove(task)

    def complete_task(self, task_id: str) -> ff.EventList:
        for task in self.tasks:
            if task_id == task.id:
                task.complete_task()
                return 'TaskCompleted', task
        raise Exception(f'Task {task_id} not found in TodoList {self}')
