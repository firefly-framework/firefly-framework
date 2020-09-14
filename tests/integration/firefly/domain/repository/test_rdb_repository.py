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
from pprint import pprint

import pytest
from firefly_test.iam import User, Role, Scope


def test_pagination(registry):
    users = registry(User)
    test = users.sort(lambda u: u.name)[0:1]

    assert len(test) == 2
    assert test[0].name == 'Bob Loblaw'
    assert test[1].name == 'Davante Adams'

    test = users.sort(lambda u: u.name)[1:2]

    assert len(test) == 2
    assert test[0].name == 'Davante Adams'
    assert test[1].name == 'David Johnson'


@pytest.fixture(autouse=True)
def fixtures(registry):
    users = registry(User)
    roles = registry(Role)
    scopes = registry(Scope)

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
