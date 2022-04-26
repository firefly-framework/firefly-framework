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

import pytest
import firefly_test.todo.domain as todo
from firefly.domain.meta.build_argument_list import build_argument_list
import firefly.domain as ffd


def call1(x: str, y: int, xx: str = None, yy: float = None):
    return locals()


def test_scalar_parameters():
    assert call1(**build_argument_list({
        'x': 'foo',
        'y': 12,
        'yy': 1.2,
    }, call1)) == {'x': 'foo', 'y': 12, 'xx': None, 'yy': 1.2}

    with pytest.raises(ffd.MissingArgument):
        call1(**build_argument_list({
            'y': 12,
        }, call1, include_none_parameters=False))


def call2(user: todo.User):
    return locals()


def test_aggregate_parameter():
    id_ = str(uuid.uuid4())
    ret = call2(**build_argument_list({
        'id': id_,
        'name': 'Bob Loblaw',
        'profile': {
            'title': 'Lawyer',
        }
    }, call2))

    assert 'user' in ret
    user = ret['user']
    assert str(user.id) == id_
    assert isinstance(user.profile, todo.Profile)
    assert user.profile.title == 'Lawyer'
    assert user.name == 'Bob Loblaw'


def test_list_of_strings():
    user = todo.User(**build_argument_list({
        'name': 'Bob Loblaw',
        'tags': ['a', 'b', 'c']
    }, todo.User))

    assert len(user.tags) == 3
