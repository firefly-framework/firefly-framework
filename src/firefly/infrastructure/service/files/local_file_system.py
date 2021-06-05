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
from typing import List, Tuple

import firefly as ff


class LocalFileSystem(ff.FileSystem):
    _serializer: ff.Serializer = None

    def read(self, file_name: str):
        with open(file_name, 'rb') as fp:
            return ff.File(
                name=file_name,
                content=fp.read()
            )

    def write(self, file: ff.File, path: str = None):
        d = path or dirname(file.name)
        if not os.path.exists(d):
            pathlib.Path(d).mkdir(parents=True, exist_ok=True)
        mode = 'wb' if isinstance(file.content, bytes) else 'w'
        data = file.content
        if not isinstance(data, str):
            data = data.decode('utf-8')
        with open((path or '').rstrip('/') + '/' + file.name, mode) as fp:
            fp.write(data)

    def list(self, path: str) -> List[Tuple[str, dict]]:
        ret = []
        for (_, _, filenames) in os.walk(path):
            # TODO we should have file sizes and last_modified here
            ret.extend([
                (f, {}) for f in filenames
            ])

        return ret

    def filter(self, path: str, fields: list, criteria: ff.BinaryOp):
        if not path.lower().endswith('.json'):
            raise NotImplemented()

        file = self.read(path)
        data = self._serializer.deserialize(file.content)
        ret = []
        if not isinstance(data, list):
            data = [data]
        for d in data:
            if criteria.matches(d):
                ret.append(d)

        return ret
