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

import pytest
import firefly_test.todo.domain as todo


def test_search_by_associate_id(user, users):
    assert users.find(lambda u: u.profile.id == user.profile.id) == user


def test_starts_with(user, users):
    assert users.find(lambda u: u.name.startswith('Bob')) == user


def test_ends_with(user, users):
    assert users.find(lambda u: u.name.endswith('Loblaw')) == user


def test_contains(user, users):
    assert users.find(lambda u: u.name.contains('Lob')) == user


def test_lower(user, users):
    assert users.find(lambda u: u.name.lower().startswith('bob')) == user
    assert users.find(lambda u: u.name.lower() == 'bob loblaw') == user


def test_upper(user, users):
    assert users.find(lambda u: u.name.upper().startswith('BOB')) == user
    assert users.find(lambda u: u.name.upper() == 'BOB LOBLAW') == user


@pytest.fixture()
def user(registry):
    users = registry(todo.User)

    profile = todo.Profile(
        title="What's up folks?"
    )
    user = todo.User(
        name='Bob Loblaw',
        settings=todo.Settings(
            send_email=False
        ),
        profile=profile
    )

    users.append(user)
    users.commit()
    users.reset()

    return user


@pytest.fixture()
def users(registry):
    return registry(todo.User)
