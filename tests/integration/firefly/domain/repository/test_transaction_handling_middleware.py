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

# TODO Update these tests

from multiprocessing import Pool
import firefly_test.todo as todo
import pytest


def run_thread(num: int):
    from firefly.application.container import Container
    container = Container()
    container.kernel.boot()
    container.system_bus.invoke(
        'todo.UpdateTodoListWithSleep', {'id': '9ebe9d14-af67-43df-9596-621f678024f1', 'task_name': f'Task {num}'}
    )


# TODO This will not pass if run with the full suite, as it has a custom config.
@pytest.mark.skip
def test_concurrency(registry):
    todos = registry(todo.TodoList)
    t = todo.TodoList(
        id='9ebe9d14-af67-43df-9596-621f678024f1',
        name='My List',
        user=todo.User(name='Foo')
    )
    todos.append(t)
    todos.commit()

    with Pool(2) as p:
        p.map(run_thread, [1, 2])

    todos.reset()
    t = todos.find(t.id)
    assert len(t.tasks) == 2


@pytest.fixture(scope="session")
def config(config):
    config['contexts']['todo']['storage']['services']['rdb']['connection']['host'] = '/tmp/todo.db'
    return config
