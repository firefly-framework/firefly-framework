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

import uuid
from datetime import datetime
from typing import List
from uuid import UUID

import firefly as ff
import sqlalchemy as sa
from pydantic.dataclasses import dataclass
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.orm import relationship

users_addresses = sa.Table(
    'users_addresses',
    ff.EntityBase.metadata,
    sa.Column('user', PG_UUID(as_uuid=True), sa.ForeignKey('users.id'), primary_key=True),
    sa.Column('address', PG_UUID(as_uuid=True), sa.ForeignKey('addresses.id'), primary_key=True)
)


class Task(ff.Entity):
    __tablename__ = 'tasks'

    id: UUID = sa.Column(PG_UUID(as_uuid=True), primary_key=True)
    name: str = sa.Column(sa.String)
    due_date: datetime = sa.Column(sa.DateTime, nullable=False)
    complete: bool = sa.Column(sa.Boolean, default=False, nullable=False)
    todo_list_id: UUID = sa.Column(PG_UUID(as_uuid=True), ForeignKey('todo_lists.id'))
    todo_list: TodoList = relationship('TodoList', back_populates="tasks")

    def complete_task(self):
        self.complete = True

    def is_overdue(self):
        return datetime.now() >= self.due_date


@ff.rest.crud()
class TodoList(ff.AggregateRoot):
    __tablename__ = 'todo_lists'

    id: UUID = sa.Column(PG_UUID(as_uuid=True), primary_key=True)
    name: str = sa.Column(sa.String(length=128), nullable=True)
    user_id: UUID = sa.Column(PG_UUID(as_uuid=True), ForeignKey('users.id'))

    tasks: List[Task] = relationship(Task, back_populates="todo_list")
    user: User = relationship('User', back_populates='todo_lists')

    def __post_init__(self):
        if self.name is None:
            self.name = f"{self.user.name}'s TODO List"

    def add_task(self, task: Task) -> ff.EventList:
        self.tasks.append(task)
        return 'TaskAdded', task

    def remove_task(self, task: Task):
        self.tasks.remove(task)

    def complete_task(self, task_id: str) -> ff.EventList:
        for task in self.tasks:
            if task_id == task.id:
                task.complete_task()
                return 'TaskCompleted', task
        raise Exception(f'Task {task_id} not found in TodoList {self}')


class Settings(ff.Entity):
    __tablename__ = 'settings'

    id: UUID = sa.Column(PG_UUID(as_uuid=True), primary_key=True)
    send_email: bool = sa.Column(sa.Boolean)
    user_id: UUID = sa.Column(PG_UUID(as_uuid=True), ForeignKey('users.id'))
    user: User = relationship('User', back_populates='settings')


class Profile(ff.AggregateRoot):
    __tablename__ = 'profiles'

    id: UUID = sa.Column(PG_UUID(as_uuid=True), primary_key=True)
    title: str = sa.Column(sa.String)
    user_id: UUID = sa.Column(PG_UUID(as_uuid=True), ForeignKey('users.id'))
    user: User = relationship('User', back_populates='profile')


class Address(ff.AggregateRoot):
    __tablename__ = 'addresses'

    id: UUID = sa.Column(PG_UUID(as_uuid=True), primary_key=True)
    street: str = sa.Column(sa.String)
    number: int = sa.Column(sa.Integer, nullable=False)
    residents: List[User] = relationship('User', secondary=users_addresses, back_populates='addresses')


class Favorite(ff.Entity):
    __tablename__ = 'entities'

    id: UUID = sa.Column(PG_UUID(as_uuid=True), primary_key=True)
    name: str = sa.Column(sa.String, nullable=False)


class Salary(ff.ValueObject):
    amount: float
    unit: str = 'USD'


@ff.rest.crud()
class User(ff.AggregateRoot):
    __tablename__ = 'users'

    id: UUID = sa.Column(PG_UUID(as_uuid=True), primary_key=True, default=lambda: uuid.uuid4())
    name: str = sa.Column(sa.String, nullable=False)
    tags: List[str] = sa.Column(sa.ARRAY(item_type=sa.String), nullable=True)
    current_salary: Salary = sa.Column(JSONB, nullable=True)
    todo_lists: List[TodoList] = relationship('TodoList', back_populates='user')
    settings: Settings = relationship('Settings', back_populates='user', uselist=False)
    profile: Profile = relationship('Profile', back_populates='user', uselist=False)
    addresses: List[Address] = relationship('Address', secondary=users_addresses, back_populates='residents')
