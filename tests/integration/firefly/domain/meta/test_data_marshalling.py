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

import firefly_test.todo.domain as todo


def test_basic_associations():
    u_id = str(uuid.uuid4())
    p_id = str(uuid.uuid4())
    a_id1 = str(uuid.uuid4())
    a_id2 = str(uuid.uuid4())
    user = todo.User(
        id=u_id,
        name='Bob Loblaw',
        profile=todo.Profile(
            id=p_id,
            title='Lawyer'
        ),
        addresses=[
            todo.Address(id=a_id1, street='Main', number='1234'),
            todo.Address(id=a_id2, street='Second', number='5555'),
        ]
    )

    assert user.to_dict() == {'id': u_id, 'todo_lists': [], 'name': 'Bob Loblaw', 'profile': {'id': p_id, 'title': 'Lawyer', 'user': u_id}, 'addresses': [{'number': 1234, 'id': a_id1, 'residents': [u_id], 'street': 'Main'}, {'number': 5555, 'id': a_id2, 'residents': [u_id], 'street': 'Second'}], 'current_salary': None, 'settings': None}


def test_value_object():
    salary = todo.Salary.from_dict({'amount': 25_000})
    assert isinstance(salary, todo.Salary)

    d = salary.to_dict()
    assert d['amount'] == 25000.0
    assert d['unit'] == 'USD'
