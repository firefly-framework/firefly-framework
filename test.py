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

from dataclasses import fields

from firefly.application import Container
from datetime import datetime
from pprint import pprint

import firefly as ff
import regex

container = Container()

schema = {
    "title": "Example Schema",
    "type": "object",
    "properties": {
        "firstName": {
            "type": "string"
        },
        "lastName": {
            "type": "string"
        },
        "age": {
            "description": "Age in years",
            "type": "integer",
            "minimum": 0
        },
        "dogs": {
            "type": "array",
            "items": {"type": "string"},
            "maxItems": 4
        },
        "address": {
            "type": "object",
            "properties": {
                "street": {"type": "string"},
                "city": {"type": "string"},
                "state": {"type": "string"}
                },
            "required":["street", "city"]
            },
        "gender": {
            "type": "string",
            "enum": ["male", "female"]
        },
        "deceased": {
            "enum": ["yes", "no", 1, 0, "true", "false"]
            }
    },
    "required": ["firstName", "lastName"]
}

cls = container.entity_factory.from_json_schema(schema)

c = cls.from_dict({
    'first_name': 'foo',
    'last_name': 'bar',
    'address': {
        'city': 'Foo',
        'street': 'bar',
    }
})

pprint(c)
