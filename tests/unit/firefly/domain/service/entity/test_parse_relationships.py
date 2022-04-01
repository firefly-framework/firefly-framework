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

import firefly_test.todo.domain as domain
from firefly import ParseRelationships
import pytest


def test_one_to_one(sut):
    relationships = sut(domain.User)

    assert 'settings' in relationships
    assert relationships['settings']['this_side'] == 'one'
    assert relationships['settings']['other_side'] == 'one'
    assert relationships['todo_lists']['other_side'] == 'one'
    assert relationships['todo_lists']['target_property'] == 'user'


def test_many_to_one(sut):
    relationships = sut(domain.TodoList)

    print()
    pprint(relationships)


@pytest.fixture()
def sut():
    return ParseRelationships()
