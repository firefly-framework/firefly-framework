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
from pprint import pprint

import firefly as ff
import firefly_test.todo.domain as todo
import pytest


def test_create(registry, fixtures):
    users = registry(todo.User)

    settings, profile, u = fixtures
    users.append(u)

    user = users.find(u.id)

    assert isinstance(user, todo.User)
    assert user.name == 'Bob Loblaw'
    assert str(user.id) == str(u.id)
    assert str(user.settings.id) == str(settings.id)
    assert user.settings.send_email is False
    assert str(user.profile.id) == str(profile.id)
    assert user.profile.title == 'Manager'


def test_update(registry, fixtures):
    users = registry(todo.User)

    settings, profile, u = fixtures
    users.append(u)

    user = users.find(u.id)
    user.name = 'Bob Seger'
    user.settings.send_email = True
    user.profile.title = 'Singer'
    users.commit()
    users.reset()

    user = list(users).pop()
    assert user.name == 'Bob Seger'
    assert user.settings.send_email is True
    assert user.profile.title == 'Singer'


def test_delete(registry, fixtures):
    users = registry(todo.User)

    settings, profile, u = fixtures
    id_ = u.id
    users.append(u)

    user = users.find(u.id)
    users.remove(user)
    users.commit()
    users.reset()

    assert users.find(id_) is None


def test_search(registry, fixtures):
    users = registry(todo.User)
    settings, profile, u = fixtures
    users.append(u)

    assert isinstance(users.find(lambda uu: uu.name == 'Bob Loblaw'), todo.User)
    with pytest.raises(ff.NoResultFound):
        users.find(lambda uu: uu.name == 'Foobar')


@pytest.fixture()
def fixtures():
    settings = todo.Settings(send_email=False)
    profile = todo.Profile(title='Manager')
    return (
        settings,
        profile,
        todo.User(name='Bob Loblaw', settings=settings, profile=profile)
    )
