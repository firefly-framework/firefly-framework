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

from typing import List
from uuid import UUID

import firefly as ff
import firefly_test.todo.domain as domain


class Settings(ff.Entity):
    id: str = ff.id_()
    user: User = ff.required()
    send_email: bool = ff.optional(default=True)


class Profile(ff.AggregateRoot):
    id: str = ff.id_()
    user: User = ff.required()
    title: str = ff.optional()


class Address(ff.AggregateRoot):
    id: str = ff.id_()
    street: str = ff.required()
    number: int = ff.required()
    residents: List[User] = ff.list_()


class Favorite(ff.Entity):
    id: str = ff.id_()
    name: str = ff.required()


class Salary(ff.ValueObject):
    amount: float = ff.required()
    unit: str = ff.optional(default='USD')


@ff.rest.crud()
class User(ff.AggregateRoot):
    id: UUID = ff.id_()
    name: str = ff.required()
    todo_lists: List[domain.TodoList] = ff.list_()
    settings: Settings = ff.required()
    profile: Profile = ff.required()
    addresses: List[Address] = ff.list_()
    current_salary: Salary = ff.optional()
    # favorites: Dict[UUID, Favorite] = ff.dict_()
