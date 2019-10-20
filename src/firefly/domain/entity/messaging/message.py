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
from dataclasses import asdict, fields

import firefly.domain as ffd

from ..entity import dict_
from ...utils import FireflyType
from ...utils import MessageMeta


class Message(FireflyType, metaclass=MessageMeta):
    headers: dict = dict_()
    _id: str = None
    _context: str = None

    def __init__(self, **kwargs):
        raise TypeError('Message is an abstract base class')

    def get_parameters(self):
        return ffd.get_arguments(self.__init__)

    def __post_init__(self):
        if self._id is None:
            self._id = str(uuid.uuid1())
        if self._context is None:
            self._context = self.__module__.split('.')[0]

    # noinspection PyDataclass
    def to_dict(self, recursive: bool = True) -> dict:
        if recursive:
            return asdict(self)

        ret = {}
        for field_ in fields(self):
            ret[field_.name] = getattr(self, field_.name)

        return ret
