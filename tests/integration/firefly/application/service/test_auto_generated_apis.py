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
from pprint import pprint

import firefly_test.todo.domain as todo
import pytest


def test_create_user(registry, user_id):
    user = list(registry(todo.User)).pop()
    assert user.name == 'Bob Loblaw'
    assert user.settings.send_email is True
    assert user.profile.title == 'Executive'
    assert user.id == user_id


def test_update_user(system_bus, registry, user_id):
    system_bus.invoke('todo.UpdateUser', {
        'id': user_id,
        'name': 'John Doe',
    })
    user = registry(todo.User).find(user_id)
    assert user.name == 'John Doe'


def test_delete_user(system_bus, registry, user_id):
    system_bus.invoke('todo.DeleteUser', {'id': user_id})
    registry(todo.User).reset()
    assert registry(todo.User).find(user_id) is None


def test_read_users(system_bus, registry):
    system_bus.invoke(
        'todo.CreateUser', {'name': 'Bob Loblaw', 'settings': {'send_email': False}, 'profile': {'title': 'Lawyer'}}
    )
    system_bus.invoke(
        'todo.CreateUser', {'name': 'John Doe', 'settings': {'send_email': False}, 'profile': {'title': 'Anonymous'}}
    )
    system_bus.invoke(
        'todo.CreateUser', {'name': 'Jane Doe', 'settings': {'send_email': False}, 'profile': {'title': 'Anonymous'}}
    )

    users = system_bus.request('todo.Users', lambda u: u.name == 'Bob Loblaw')
    assert len(users) == 1
    assert users[0]['name'] == 'Bob Loblaw'

    users = system_bus.request('todo.Users', lambda u: u.name.startswith('J'))
    assert len(users) == 2


@pytest.fixture()
def user_id(system_bus):
    id_ = uuid.uuid4()
    system_bus.invoke('todo.CreateUser', {
        'id': id_,
        'name': 'Bob Loblaw',
        'settings': {
            'send_email': True,
        },
        'profile': {
            'title': 'Executive',
        },
    })
    return id_
