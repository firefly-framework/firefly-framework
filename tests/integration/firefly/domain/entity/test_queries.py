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

from test_src.iam.domain.entity import User


def test_query_todos(system_bus, message_factory):
    users = system_bus.query(message_factory.query('iam.Users'))
    assert len(users) == 2


def test_search_criteria_equals(system_bus, message_factory):
    search_criteria = User.c.name == 'foo'
    users = system_bus.query(message_factory.query('iam.Users', {'criteria': search_criteria.to_dict()}))
    assert len(users) == 1


def test_search_criteria_greater_than(system_bus, message_factory):
    search_criteria = User.c.name > 'car'
    users = system_bus.query(message_factory.query('iam.Users', {'criteria': search_criteria.to_dict()}))
    assert len(users) == 1


def test_search_criteria_or(system_bus, message_factory):
    search_criteria = (User.c.name == 'foo') | (User.c.name == 'bar')
    users = system_bus.query(message_factory.query('iam.Users', {'criteria': search_criteria.to_dict()}))
    assert len(users) == 2


@pytest.fixture(autouse=True)
def fixture_data(registry):
    r = registry(User)
    r.add(User(name='foo', email='foo@bar.com'))
    r.add(User(name='bar', email='bar@baz.com'))
