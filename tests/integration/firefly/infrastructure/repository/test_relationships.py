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
from pprint import pprint

import firefly_test.todo.domain as todo
import pytest


def test_one_to_one(registry):
    users = registry(todo.User)
    profiles = registry(todo.Profile)

    user = todo.User(
        name='Bob Loblaw',
        settings=todo.Settings(
            send_email=False
        ),
        profile=todo.Profile(
            title="What's up folks?"
        )
    )

    assert isinstance(user.settings, todo.Settings)
    assert isinstance(user.settings.user, todo.User)
    assert user.settings.send_email is False
    assert user.profile.title == "What's up folks?"

    users.append(user)
    user: todo.User = users.find(user.id)

    assert isinstance(user.settings, todo.Settings)
    assert isinstance(user.settings.user, todo.User)
    assert user.settings.send_email is False
    assert user.profile.title == "What's up folks?"

    profile = profiles.find(user.profile.id)
    assert isinstance(profile, todo.Profile)
    assert isinstance(profile.user, todo.User)
    assert isinstance(profile.user.settings, todo.Settings)
    assert profile.title == "What's up folks?"


def test_one_to_one_missing_one_side(registry):
    with pytest.raises(TypeError):
        user = todo.User(
            name='Bob Loblaw',
            settings=todo.Settings(
                send_email=False
            )
        )
        registry(todo.User).append(user)


def test_many_to_one(registry):
    users = registry(todo.User)

    user = todo.User(
        name='Bob Loblaw',
        settings=todo.Settings(
            send_email=True
        ),
        profile=todo.Profile(
            title='My Title'
        )
    )
    todo_list = todo.TodoList(
        user=user,
        name='Bobs list',
        tasks=[
            todo.Task(name='Do stuff', due_date=datetime.now())
        ]
    )
    users.append(user)
    users.commit()
    users.reset()
    user = users.find(user.id)

    print(user)
    assert len(user.todo_lists) == 1
    assert str(user.todo_lists[0].id) == str(todo_list.id)


def test_many_to_many(registry):
    users = registry(todo.User)
    addresses = registry(todo.Address)

    user_1 = todo.User(
        name='Bob Loblaw',
        settings=todo.Settings(send_email=True),
        profile=todo.Profile(title='My Title')
    )
    user_2 = todo.User(
        name='John',
        settings=todo.Settings(send_email=True),
        profile=todo.Profile(title='My Title')
    )
    user_3 = todo.User(
        name='Jane',
        settings=todo.Settings(send_email=True),
        profile=todo.Profile(title='My Title')
    )
    user_4 = todo.User(
        name='Jimmy',
        settings=todo.Settings(send_email=True),
        profile=todo.Profile(title='My Title')
    )

    address_1 = todo.Address(
        street='main',
        number=1234
    )
    address_2 = todo.Address(
        street='main',
        number=1235
    )

    address_1.residents.append(user_1)
    address_1.residents.append(user_4)
    address_2.residents.append(user_2)
    address_2.residents.append(user_3)
    address_2.residents.append(user_4)

    users.append(user_1)
    users.append(user_2)
    users.append(user_3)
    users.append(user_4)

    address_1 = addresses.find(address_1.id)
    address_2 = addresses.find(address_2.id)

    assert len(address_1.residents) == 2
    assert len(address_2.residents) == 3

    jimmy = users.find(user_4.id)
    assert len(jimmy.addresses) == 2


# Hash mapping is implemented, but marshmallow-sqlalchemy doesn't seem to handle it that well. I don't think we'll need
# this feature anyway, but if we do it'll take some work to get it going properly.
#
# def test_hash_mapping(registry):
#     users = registry(todo.User)
#     favorite1 = todo.Favorite(name='foo')
#     favorite2 = todo.Favorite(name='bar')
#     favorite3 = todo.Favorite(name='baz')
#     favorite4 = todo.Favorite(name='biz')
#
#     user = todo.User(
#         name='Bob Loblaw',
#         settings=todo.Settings(send_email=True),
#         profile=todo.Profile(title='My Title'),
#         favorites={
#             favorite1.id: favorite1,
#             favorite2.id: favorite2,
#             favorite3.id: favorite3,
#             favorite4.id: favorite4,
#         }
#     )
#     id_ = user.id
#     users.append(user)
#
#     user = users.find(id_)
#     assert len(user.favorites.keys()) == 4
