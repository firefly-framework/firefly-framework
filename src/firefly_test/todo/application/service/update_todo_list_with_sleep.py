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

from datetime import datetime
from time import sleep

import firefly as ff
import firefly_test.todo as todo


@ff.command_handler()
class UpdateTodoListWithSleep(ff.ApplicationService):
    _registry: ff.Registry = None

    def __call__(self, id_: str, task_name: str, **kwargs):
        todo_list: todo.TodoList = self._registry(todo.TodoList).find(id_)
        sleep(1)
        todo_list.tasks.append(todo.Task(name=task_name, due_date=datetime.now()))
