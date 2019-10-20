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

from typing import Callable

import pytest
from firefly import MiddlewareStack, Middleware, Message, Command


def test_order(sut):
    result = sut(Command())
    assert result.headers['numbers'] == [1, 2, 3]


@pytest.fixture()
def sut():
    class AppendNumber(Middleware):
        def __init__(self, number: int):
            self.number = number

        def __call__(self, message: Message, next_: Callable, *args, **kwargs):
            if 'numbers' not in message.headers:
                message.headers['numbers'] = []
            message.headers['numbers'].append(self.number)
            return next_(message)

    return MiddlewareStack([
        AppendNumber(1),
        AppendNumber(2),
        AppendNumber(3),
    ])
