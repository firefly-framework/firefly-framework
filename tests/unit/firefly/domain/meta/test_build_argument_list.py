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

from typing import List

import firefly as ff


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
