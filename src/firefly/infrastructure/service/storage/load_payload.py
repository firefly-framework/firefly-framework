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

import bz2

import firefly.domain as ffd


class LoadPayload:
    _s3_client = None
    _serializer: ffd.Serializer = None
    _bucket: str = None

    def __call__(self, key: str):
        response = self._s3_client.get_object(
            Bucket=self._bucket,
            Key=key
        )
        data = response['Body'].read()
        if key.endswith('bz2'):
            data = bz2.decompress(data)
        return self._serializer.deserialize(data)
