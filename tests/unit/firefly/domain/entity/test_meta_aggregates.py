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

import firefly as ff
import pytest


def test_meta_aggregate(schema):
    a: ff.MetaAggregate = ff.MetaAggregate(
        data={
            'name': 'John Doe',
            'integer': 1,
            'number': 1.1,
            'boolean': True,
            'null': None,
            'array_of_numbers': [1, 2, 3],
            'child_object': {
                'child_name': 'Jane Doe',
                'child_enum': 'one'
            }
        },
        schema=schema
    )

    assert a.name == 'John Doe'
    assert a.integer == 1
    assert a.number == 1.1
    assert a.boolean is True
    assert a.null is None
    assert a.array_of_numbers == [1, 2, 3]
    assert a.child_object.child_name == 'Jane Doe'
    assert a.child_object.child_enum == 'one'


def test_required_fields(schema):
    with pytest.raises(ff.MissingArgument, match='.*name is required.*'):
        ff.MetaAggregate(
            data={},
            schema=schema
        )


@pytest.fixture()
def schema():
    return ff.JsonSchema(schema=json.loads("""
{
    "type": "object",
    "properties": {
        "name": {
            "type": "string"
        },
        "integer": {
            "type": "integer"
        },
        "number": {
            "type": "number"
        },
        "boolean": {
            "type": "boolean"
        },
        "null": {
            "type": "null"
        },
        "array_of_numbers": {
            "type": "array",
            "items": {
                "type": "number"
            }
        },
        "child_object": {
            "type": "object",
            "properties": {
                "child_name": {
                    "type": "string"
                },
                "child_enum": {
                    "enum": [
                        "one",
                        "two",
                        "three"
                    ]
                }
            }
        }
    },
    "required": [
        "name"
    ],
    "title": "Test Schema"
}
    """))
