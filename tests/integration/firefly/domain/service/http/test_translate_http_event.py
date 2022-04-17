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
import json
import pathlib

import pytest


def test_get_with_single_path_parameter(sut, load):
    assert sut(load('1_input')) == load('1_output')


@pytest.fixture()
def sut(kernel):
    return kernel.translate_http_event


@pytest.fixture()
def load():
    def do_load(file):
        with open(f'{pathlib.Path(__file__).parent.absolute()}/data/{file}.json', 'r') as fp:
            return json.loads(fp.read())
    return do_load
