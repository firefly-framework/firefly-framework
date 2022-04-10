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

import firefly_test.todo.domain as todo


def test_event_listener(system_bus):
    # TODO Set this up with an actual assertion
    system_bus.dispatch('todo.UserCreated', {
        'id': 'e6a593ff-b7ed-44ff-8d01-b2c911a5c50c',
        'name': 'Bob Loblaw',
    })


def test_command_handler(system_bus):
    response = system_bus.invoke('todo.DemandAHello', {'name': 'Bob'})
    assert response == 'Hello, Bob!!'


def test_query_handler(system_bus):
    user = todo.User(name='Bob')
    response = system_bus.request('todo.Salutations', data={'user': user})
    assert response == 'Salutations, Bob!!'
