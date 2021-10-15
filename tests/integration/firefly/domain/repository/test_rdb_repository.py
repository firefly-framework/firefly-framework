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

import firefly.tests.rdb_repository as tests
from firefly_test.iam import User, Role, Scope
from firefly_test.todo import TodoList


def test_mutability(registry):
    users = registry(User)
    roles = registry(Role)
    scopes = registry(Scope)

    users.migrate_schema()
    roles.migrate_schema()
    scopes.migrate_schema()

    tests.iam_fixtures(users, roles, scopes)

    tests.test_mutability(users)


def test_basic_crud_operations(registry):
    tests.test_basic_crud_operations(registry(TodoList))


def test_aggregate_associations(registry):
    users = registry(User)
    roles = registry(Role)
    scopes = registry(Scope)

    users.migrate_schema()
    roles.migrate_schema()
    scopes.migrate_schema()

    tests.iam_fixtures(users, roles, scopes)

    tests.test_aggregate_associations(users)


def test_pagination(registry):
    users = registry(User)
    roles = registry(Role)
    scopes = registry(Scope)

    users.migrate_schema()
    roles.migrate_schema()
    scopes.migrate_schema()

    tests.iam_fixtures(users, roles, scopes)

    tests.test_pagination(users)


def test_list_expansion(registry):
    users = registry(User)
    roles = registry(Role)
    scopes = registry(Scope)

    users.migrate_schema()
    roles.migrate_schema()
    scopes.migrate_schema()

    tests.iam_fixtures(users, roles, scopes)

    tests.test_list_expansion(users)
