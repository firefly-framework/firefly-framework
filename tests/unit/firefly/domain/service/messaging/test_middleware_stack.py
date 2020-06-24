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
from firefly import MiddlewareStack, Message, Middleware, domain as ffd


class MyMessage(Message):
    pass


class MyMiddleware1(Middleware):

    def __call__(self, message: ffd.Message, next_: Callable) -> ffd.Message:
        return message


class MyMiddleware2(Middleware):

    def __call__(self, message: ffd.Message, next_: Callable) -> ffd.Message:
        return message


class MyMiddleware3(Middleware):

    def __call__(self, message: ffd.Message, next_: Callable) -> ffd.Message:
        return message


class MyMiddleware4(Middleware):

    def __call__(self, message: ffd.Message, next_: Callable) -> ffd.Message:
        return message


def test_empty(sut):
    m = MyMessage()
    assert sut(m) is m


def test_replace(sut):
    sut.add(MyMiddleware1())
    sut.add(MyMiddleware2())
    sut.add(MyMiddleware3())

    assert sut.middleware[1].__class__ is MyMiddleware2

    sut.replace(MyMiddleware2, MyMiddleware4())

    assert sut.middleware[1].__class__ is MyMiddleware4


@pytest.fixture()
def sut():
    return MiddlewareStack([])
