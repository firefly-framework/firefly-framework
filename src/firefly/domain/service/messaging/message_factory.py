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

from dataclasses import make_dataclass, fields, is_dataclass, asdict
from typing import Union, TypeVar, Type, Tuple, get_type_hints

import firefly.domain as ffd

from ...entity.messaging.message import Message

M = TypeVar('M', bound=Message)
MessageBase = Type[M]


class MessageFactory:
    @staticmethod
    def convert_type(message: Message, new_name: str, new_base: Union[MessageBase, Tuple[MessageBase]]):
        if not is_dataclass(message):
            raise ffd.FrameworkError('message must be a dataclass')

        types = get_type_hints(message.__class__)
        message_fields = []
        for field_ in fields(message):
            message_fields.append((field_.name, types[field_.name], field_))

        if not isinstance(new_base, tuple):
            new_base = (new_base,)

        cls = make_dataclass(new_name, fields=message_fields, bases=new_base, eq=False, repr=False)

        return cls(**asdict(message))

    def event(self, name: str, data: dict = None):
        return self._build(name, data or {}, (ffd.Event,))

    def command(self, name: str, data: dict = None):
        return self._build(name, data or {}, (ffd.Command,))

    def query(self, name: str, criteria: ffd.BinaryOp = None, data: dict = None):
        data = data or {}
        if criteria is not None:
            data['criteria'] = criteria.to_dict()
        return self._build(name, data, (ffd.Query,))

    @staticmethod
    def _build(name: str, data: dict, bases: tuple):
        if '.' in name:
            context, name = name.split('.')
            data['_context'] = context
        annotations_ = {k: type(v) for k, v in data.items()}

        class DynamicMessage(*bases, fields_=data, annotations_=annotations_):
            pass
        DynamicMessage.__name__ = name

        return DynamicMessage(**data)
