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
import json

import pytest

from firefly_test.iam.domain import User


def test_query_todos(system_bus, message_factory):
    users = system_bus.request('iam.Users')
    assert len(users) == 2


def test_search_criteria_equals(system_bus):
    users = system_bus.request('iam.Users', lambda u: u.name == 'foo')
    assert len(users) == 1


def test_search_criteria_greater_than(system_bus, message_factory):
    search_criteria = User.c.name > 'car'
    users = system_bus.request('iam.Users', search_criteria)
    assert len(users) == 1


def test_search_criteria_or(system_bus, message_factory):
    search_criteria = ((User.c.name == 'foo') | (User.c.name == 'bar'))
    users = system_bus.request('iam.Users', search_criteria)
    assert len(users) == 2


@pytest.fixture(autouse=True)
def fixture_data(registry):
    r = registry(User)
    for u in list(r):
        r.remove(u)
    r.commit()
    r.reset()
    r.append(User(name='foo', email='foo@bar.com'))
    r.append(User(name='bar', email='bar@baz.com'))
    r.commit()
