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

from datetime import datetime
from typing import List

import firefly as ff
from firefly_test.todo import TodoList


class BaseClass(ff.ValueObject):
    base_field: str = ff.optional()


class Foo(BaseClass):
    foo_field: str = ff.optional()


class Bar(BaseClass):
    bar_field: str = ff.optional()


class Widget(ff.AggregateRoot):
    stuff: List[BaseClass] = ff.list_()


class Widget2(ff.AggregateRoot):
    foo: BaseClass = ff.optional()


class ChildWidget(ff.ValueObject):
    name: str = ff.required()
    extra1: str = ff.optional()
    extra2: str = ff.optional()


class ParentWidget(ff.AggregateRoot):
    id: str = ff.id_()
    name: str = ff.required()
    child: ChildWidget = ff.optional()


def test_class_hierarchies(serializer):
    w = Widget(stuff=[Foo(foo_field='foo'), Bar(bar_field='bar')])
    data = serializer.deserialize(serializer.serialize(w))
    nw: Widget = Widget.from_dict(data)

    assert isinstance(nw.stuff[0], Foo)
    assert isinstance(nw.stuff[1], Bar)

    w = Widget2(foo=Bar(bar_field='bar'))
    data = serializer.deserialize(serializer.serialize(w))
    nw: Widget2 = Widget2.from_dict(data)

    assert isinstance(nw.foo, Bar)


def test_reserved_words():
    def foo(id_: str):
        pass

    args = ff.build_argument_list({'id': 'bar'}, foo)

    assert 'id_' in args and args['id_'] == 'bar'


def test_todos():
    todo = TodoList.from_dict({
        'id': 'abc123',
        'user': {"id": "cf130627-c5d9-4ccf-bee3-2fe96a675b53", "name": "Bob"},
        'name': "Bob's TODO List",
        'tasks': []
    })

    assert todo.name == "Bob's TODO List"
    assert todo.tasks == []


def test_shared_property_names_in_nested_classes():
    p = ParentWidget.from_dict({
        'name': 'foo',
    })

    assert p.name == 'foo'


def test_optional_datetimes():
    class TestAppService(ff.ApplicationService):
        def __call__(self, last_updated: datetime = None, start_date: datetime = None, **kwargs):
            pass

    sut = TestAppService()
    x = ff.build_argument_list({
        'last_updated': '2021-05-26T06:20:15'
    }, sut)

    assert isinstance(x['last_updated'], datetime) is True
