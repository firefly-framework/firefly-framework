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

import test_src.calendar.domain as calendar
import test_src.todo.domain as todo


def test_create_on_event(system_bus, registry, message_factory):
    system_bus.invoke(message_factory.command('iam.CreateUser', {
        'name': 'foo',
        'email': 'foo@bar.com',
    }))

    todos = registry(todo.TodoList).all()
    assert len(todos) == 1
    assert todos[0].user.name == 'foo'
    assert todos[0].name == "foo's TODO List"

    calendars = registry(calendar.Calendar).all()
    assert len(calendars) == 1


def test_delete_on_event(system_bus, registry, message_factory):
    system_bus.invoke(message_factory.command('iam.CreateUser', {
        'name': 'foo',
        'email': 'foo@bar.com',
    }))

    todos = registry(todo.TodoList).all()
    assert len(todos) == 1

    system_bus.invoke(message_factory.command('iam.DeleteUser', {
        'id': todos[0].id,
    }))

    assert len(registry(todo.TodoList).all()) == 0


def test_application_service_event(system_bus, registry, message_factory):
    system_bus.invoke(message_factory.command('iam.CreateUser', {
        'name': 'foo',
        'email': 'foo@bar.com',
    }))

    assert len(registry(calendar.Calendar).all()) == 1
