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

import firefly_test.todo.domain as domain
import firefly as ff


def test_registry_support(registry):
    def my_func(todo_list: domain.TodoList):
        assert isinstance(todo_list, ff.AggregateRoot)
        assert todo_list.id == 'abc123'

    lists = registry(domain.TodoList)
    lists.append(domain.TodoList(id='abc123', user={'name': 'Bob'}, name='My List'))
    lists.commit()

    my_func(**ff.build_argument_list({'todo_list': 'abc123'}, my_func, registry=registry))
