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
from datetime import datetime, timedelta


async def test_fail_one_check(container, client, serializer):
    response = await client.post(f'/todo-lists/abc123/task', data=serializer.serialize({
        'headers': {
            'fail_authentication': True,
        },
        'todo_list': 'abc123',
        'name': 'my new task',
        'due_date': datetime.now() + timedelta(days=1)
    }))

    assert response.status != 403


async def test_fail_both_checks(container, client, serializer):
    response = await client.post(f'/todo-lists/abc123/task', data=serializer.serialize({
        'headers': {
            'fail_authentication': True,
            'fail_authentication2': True,
        },
        'todo_list': 'abc123',
        'name': 'my new task',
        'due_date': datetime.now() + timedelta(days=1)
    }))

    assert response.status == 403
