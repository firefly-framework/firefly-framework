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

import uuid
from datetime import datetime
from multiprocessing import Pool
from pprint import pprint

from firefly_test.iam import Scope, Role, User
from firefly_test.todo import TodoList, User as TodoUser, Task

id_ = str(uuid.uuid4())


def test_mutability(users):
    subset = users.filter(lambda u: u.name == 'Bob Loblaw')

    assert len(users) == 4
    assert len(subset) == 1
    assert subset[0].name == 'Bob Loblaw'
    assert len(users.filter(lambda u: u.email.is_in(('davante@adams.com', 'bob@loblaw.com')))) == 2
    assert len(users) == 4

    half = users.sort(lambda u: u.name)[2:]
    assert len(half) == 2
    assert half[0].name == 'David Johnson'
    assert half[1].name == 'John Doe'

    bob = users.filter(lambda u: u.name == 'Bob Loblaw')[0]
    bob.email = 'foo@bar.com'
    users.commit()
    assert users.find(lambda u: u.name == 'Bob Loblaw').email == 'foo@bar.com'

    subset = users.filter(lambda u: u.email.is_in(('davante@adams.com', 'bob@loblaw.com'))).sort(lambda u: u.email)
    subset.remove(subset[0])
    users.commit()
    assert len(users) == 3


def test_basic_crud_operations(todos):
    todos.migrate_schema()

    todos.append(TodoList(id=id_, user=TodoUser(name='Bob')))
    todos.commit()
    todos.reset()

    assert len(todos) == 1
    todo: TodoList = todos.find(id_)
    assert todo is not None
    assert todo.user.name == 'Bob'

    todo.tasks.append(Task(name='Task 1', due_date=datetime.now()))
    todos.commit()
    todos.reset()

    assert len(todos) == 1
    todo: TodoList = todos.find(id_)
    assert len(todo.tasks) == 1

    todo.user.name = 'Phillip'
    todos.commit()
    todos.reset()

    assert len(todos) == 1
    todo: TodoList = todos.find(id_)
    assert todo.user.name == 'Phillip'

    todos.remove(todo)
    todos.commit()
    todos.reset()

    assert len(todos) == 0
    assert todos.find(id_) is None


def test_aggregate_associations(users):
    bob = users.find(lambda u: u.name == 'Bob Loblaw')

    assert bob.roles[0].name == 'Admin User'
    assert bob.roles[0].scopes[0].id == 'firefly.admin'


def test_pagination(users):
    test = users.sort(lambda u: u.name)[0:1]

    assert len(test) == 2
    assert test[0].name == 'Bob Loblaw'
    assert test[1].name == 'Davante Adams'

    test = users.sort(lambda u: u.name)[1:2]

    assert len(test) == 2
    assert test[0].name == 'Davante Adams'
    assert test[1].name == 'David Johnson'

    test = users.sort(lambda u: u.name).filter(lambda u: u.name.is_in(('Davante Adams', 'David Johnson')))
    assert test[0].name == 'Davante Adams'
    assert test[1].name == 'David Johnson'


def test_list_expansion(users):
    my_users = users.filter(lambda u: u.name.is_in(['Bob Loblaw', 'Davante Adams']))

    emails = list(map(lambda u: u.email, my_users))
    emails.sort()
    assert emails == ['bob@loblaw.com', 'davante@adams.com']

    my_users = list(filter(lambda u: u.name == 'Bob Loblaw', users))
    assert len(my_users) == 1
    assert my_users[0].name == 'Bob Loblaw'


def iam_fixtures(users, roles, scopes):
    my_scopes = [
        Scope(id='firefly.admin'),
        Scope(id='firefly.read'),
        Scope(id='firefly.write'),
    ]
    list(map(lambda s: scopes.append(s), my_scopes))
    scopes.commit()

    my_roles = [
        Role(name='Anonymous User', scopes=[my_scopes[1]]),
        Role(name='Admin User', scopes=[my_scopes[0]]),
        Role(name='Regular User', scopes=[my_scopes[1], my_scopes[2]]),
    ]
    list(map(lambda r: roles.append(r), my_roles))
    roles.commit()

    users.append(User(name='John Doe', email='john@doe.com', roles=[my_roles[2]]))
    users.append(User(name='Bob Loblaw', email='bob@loblaw.com', roles=[my_roles[1]]))
    users.append(User(name='David Johnson', email='david@johnson.com', roles=[my_roles[1], my_roles[2]]))
    users.append(User(name='Davante Adams', email='davante@adams.com', roles=[my_roles[0]]))
    users.commit()

    users.reset()
    roles.reset()
    scopes.reset()
