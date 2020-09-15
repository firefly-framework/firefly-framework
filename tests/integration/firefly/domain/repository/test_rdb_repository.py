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
from datetime import datetime

import pytest
from firefly_test.iam import User, Role, Scope
from firefly_test.todo import TodoList, Task, User as TodoUser


def test_basic_crud_operations(registry):
    do_test_basic_crud_operations(registry(TodoList))


def do_test_basic_crud_operations(todos):
    todos.migrate_schema()

    todos.append(TodoList(id='abc123', user=TodoUser(name='Bob')))
    todos.commit()
    todos.reset()

    assert len(todos) == 1
    todo: TodoList = todos.find('abc123')
    assert todo is not None
    assert todo.user.name == 'Bob'

    todo.tasks.append(Task(name='Task 1', due_date=datetime.now()))
    todos.commit()
    todos.reset()

    assert len(todos) == 1
    todo: TodoList = todos.find('abc123')
    assert len(todo.tasks) == 1

    todo.user.name = 'Phillip'
    todos.commit()
    todos.reset()

    assert len(todos) == 1
    todo: TodoList = todos.find('abc123')
    assert todo.user.name == 'Phillip'

    todos.remove(todo)
    todos.commit()
    todos.reset()

    assert len(todos) == 0
    assert todos.find('abc123') is None


def test_aggregate_associations(registry):
    users = registry(User)
    roles = registry(Role)
    scopes = registry(Scope)
    do_test_aggregate_associations(users, roles, scopes)


def do_test_aggregate_associations(users, roles, scopes):
    users.migrate_schema()
    roles.migrate_schema()
    scopes.migrate_schema()

    iam_fixtures(users, roles, scopes)

    bob = users.find(lambda u: u.name == 'Bob Loblaw')
    print(bob)

    assert bob.roles[0].name == 'Admin User'
    assert bob.roles[0].scopes[0].id == 'firefly.admin'


def test_pagination(registry):
    do_test_pagination(registry(User))


def do_test_pagination(users):
    test = users.sort(lambda u: u.name)[0:1]

    assert len(test) == 2
    assert test[0].name == 'Bob Loblaw'
    assert test[1].name == 'Davante Adams'

    test = users.sort(lambda u: u.name)[1:2]

    assert len(test) == 2
    assert test[0].name == 'Davante Adams'
    assert test[1].name == 'David Johnson'


def iam_fixtures(users, roles, scopes):
    scopes.append(Scope(id='firefly.admin'))
    scopes.append(Scope(id='firefly.read'))
    scopes.append(Scope(id='firefly.write'))
    scopes.commit()

    roles.append(Role(name='Anonymous User', scopes=[scopes[1]]))
    roles.append(Role(name='Admin User', scopes=[scopes[0]]))
    roles.append(Role(name='Regular User', scopes=[scopes[1], scopes[2]]))
    roles.commit()

    users.append(User(name='John Doe', email='john@doe.com', roles=[roles[2]]))
    users.append(User(name='Bob Loblaw', email='bob@loblaw.com', roles=[roles[1]]))
    users.append(User(name='David Johnson', email='david@johnson.com', roles=[roles[1], roles[2]]))
    users.append(User(name='Davante Adams', email='davante@adams.com', roles=[roles[0]]))
    users.commit()
