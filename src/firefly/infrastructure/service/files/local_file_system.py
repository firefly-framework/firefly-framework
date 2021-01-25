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

from __future__ import annotations

import os
import pathlib
from os.path import dirname

import firefly as ff


class LocalFileSystem(ff.FileSystem):
    def read(self, file_name: str):
        with open(file_name, 'rb') as fp:
            return fp.read()

    def write(self, file_name: str, data):
        d = dirname(file_name)
        if not os.path.exists(d):
            pathlib.Path(d).mkdir(parents=True, exist_ok=True)
        mode = 'wb' if isinstance(data, bytes) else 'w'
        with open(file_name, mode) as fp:
            fp.write(data)
