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

from typing import Union, Any

from ..entity import Entity, id_, dict_, required


class Envelope(Entity):
    id: str = id_()
    headers: dict = dict_()
    raw_request: dict = dict_()
    body: Any = required()

    @classmethod
    def wrap(cls, body: Any) -> Envelope:
        return cls(body=body)

    def unwrap(self):
        return self.body

    def set_requested_content_type(self, type_: str):
        self.headers['accept'] = type_
        return self

    def get_requested_content_type(self):
        return self.headers.get('accept')

    def set_raw_request(self, source_headers: Any):
        self.raw_request = source_headers
        return self

    def get_raw_request(self):
        return self.raw_request

    def set_range(self, lower: int, upper: int, total: int, unit: str = None):
        self.headers['range'] = {
            'lower': lower,
            'upper': upper,
            'total': total,
        }
        if unit is not None:
            self.headers['range']['unit'] = unit
        return self

    def get_range(self):
        return self.headers.get('range')

    def add_forwarding_address(self, location: str):
        self.headers['location'] = location
        return self
