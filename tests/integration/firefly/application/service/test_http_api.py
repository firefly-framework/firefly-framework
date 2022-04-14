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
from firefly import EntityAttributeSpy


def test_create_user(registry, user_id):
    user = registry(todo.User).find(user_id)
    assert user.id == user_id
    assert user.name == 'Bob Loblaw'


def test_update_user(client, registry, serializer, user_id):
    client.put(f'/todo/users/{user_id}', body=serializer.serialize({
        'name': 'John Doe'
    }))
    user = registry(todo.User).find(user_id)
    assert user.name == 'John Doe'


def test_delete_user(client, registry, user_id):
    client.delete(f'/todo/users/{user_id}')
    registry(todo.User).reset()
    assert registry(todo.User).find(user_id) is None


def test_read_users(client, registry, serializer):
    client.post(f'/todo/users', body=serializer.serialize(
        {'name': 'Bob Loblaw', 'settings': {'send_email': False}, 'profile': {'title': 'Lawyer'}}
    ))
    client.post(f'/todo/users', body=serializer.serialize(
        {'name': 'John Doe', 'settings': {'send_email': False}, 'profile': {'title': 'Anonymous'}}
    ))
    client.post(f'/todo/users', body=serializer.serialize(
        {'name': 'Jane Doe', 'settings': {'send_email': False}, 'profile': {'title': 'Anonymous'}}
    ))

    criteria = (lambda u: u.name == 'Bob Loblaw')(EntityAttributeSpy())
    response = client.get('/todo/users', body=serializer.serialize({
        'criteria': criteria,
    }))
    users = serializer.deserialize(response.body)

    assert len(users) == 1
    assert users[0]['name'] == 'Bob Loblaw'

    criteria = (lambda u: u.name.startswith('J'))(EntityAttributeSpy())
    response = client.get('/todo/users', body=serializer.serialize({
        'criteria': criteria,
    }))
    users = serializer.deserialize(response.body)
    assert len(users) == 2


@pytest.fixture()
def user_id(client, serializer):
    id_ = uuid.uuid4()
    client.post('/todo/users', body=serializer.serialize({
        'id': id_,
        'name': 'Bob Loblaw',
        'settings': {
            'send_email': True,
        },
        'profile': {
            'title': 'Executive',
        },
    }))

    return id_
