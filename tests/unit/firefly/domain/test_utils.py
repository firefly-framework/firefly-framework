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
import typing


def test_is_type_hint():
    assert ff.is_type_hint(typing.List[str])
    assert ff.is_type_hint(typing.Dict[str, str])
    assert ff.is_type_hint(typing.Union[typing.List[str], str])
    assert ff.is_type_hint(ff.get_args(typing.Union[typing.List[str], str])[0])


def test_get_origin():
    assert ff.get_origin(typing.List[str]) == typing.List
    assert ff.get_origin(typing.Dict[str, str]) is typing.Dict
    assert ff.get_origin(typing.Union[typing.List[str], str]) is typing.Union


def test_get_args():
    assert ff.get_args(typing.List[str]) == (str,)
    assert ff.get_args(typing.Dict[str, str]) == (str, str)
    assert ff.get_args(typing.Union[typing.List[str], str]) == (typing.List[str], str)
