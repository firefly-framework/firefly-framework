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

from typing import List

import firefly as ff

from .task import Task
from .user import User


@ff.rest.crud()
class TodoList(ff.AggregateRoot, create_on='iam.UserCreated', delete_on='iam.UserDeleted'):
    id: str = ff.id_()
    user: User = ff.required()
    name: str = ff.optional(index=True, length=128)
    tasks: List[Task] = ff.list_()

    def __post_init__(self):
        if self.name is None:
            self.name = f"{self.user.name}'s TODO List"

    @ff.rest('/task', method='POST')
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
