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

from datetime import datetime, timedelta

import pytest

from firefly_test.todo import TodoList, User


def test_auto_generated_api(system_bus, message_factory, registry):
    system_bus.invoke('todo.TodoList::AddTask', {
        'todo_list': 'abc123',
        'name': 'my task',
        'due_date': datetime.now() + timedelta(days=1)
    })

    todo = registry(TodoList).find('abc123')
    assert len(todo.tasks) == 1
    assert todo.tasks[0].name == 'my task'


@pytest.mark.skip
def test_nested_api(system_bus, message_factory, registry):
    system_bus.invoke(message_factory.command('todo.TodoList::AddTask', {
        'todo_list': 'abc123',
        'name': 'my task',
        'due_date': datetime.now() + timedelta(days=1)
    }))

    todo = registry(TodoList).find('abc123')
    system_bus.invoke(message_factory.command('todo.TodoList::CompleteTask', {
        'todo_list': 'abc123',
        'task_id': todo.tasks[0].id,
    }))

    todo = registry(TodoList).find('abc123')
    assert todo.tasks[0].complete is True


@pytest.fixture(autouse=True)
def todo(registry, request):
    r = registry(TodoList)

    def teardown():
        for l in r:
            r.remove(l)

    request.addfinalizer(teardown)

    ret = TodoList(id="abc123", user=User(name='foo'))
    r.append(ret)
    r.commit()
    return ret
