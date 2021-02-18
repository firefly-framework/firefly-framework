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

import firefly as ff


class Config(ff.ValueObject):
    x: str = ff.optional()
    y: str = ff.optional()
    z: str = ff.optional()


class Widget(ff.AggregateRoot):
    config: Config = ff.optional()


def test_load_dict_with_nested_value_objects():
    w = Widget(config=Config(x='foo', y='bar', z='baz'))
    w.load_dict({
        'config': {
            'y': 'BAR',
        }
    })

    assert w.config.x == 'foo'
    assert w.config.y == 'BAR'
    assert w.config.z == 'baz'
