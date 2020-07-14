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

# __pragma__('skip')
from dataclasses import make_dataclass, fields, is_dataclass, asdict
from typing import Union, TypeVar, Type, Tuple, get_type_hints
# __pragma__('noskip')
# __pragma__ ('ecom')
"""?
from firefly.presentation.web.polyfills import make_dataclass, fields, is_dataclass, asdict, Union, TypeVar, Type, Tuple, get_type_hints
?"""
# __pragma__ ('noecom')

import firefly.domain as ffd

from firefly.domain.entity.messaging.message import Message

# __pragma__('kwargs')


class MessageFactory:
    @staticmethod
    def convert_type(message: Message, new_name: str, new_base: Union[Message, Tuple[Message]]):
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

    def event_class(self, name: str, fields_: dict = None):
        return self._build_message_class(name, fields_, (ffd.Event,))

    def command(self, name: str, data: dict = None):
        return self._build(name, data or {}, (ffd.Command,))

    def command_class(self, name: str, fields_: dict = None):
        return self._build_message_class(name, fields_, (ffd.Command,))

    def query(self, name: str, criteria: ffd.BinaryOp = None, data: dict = None):
        data = data or {}
        if criteria is not None:
            data['criteria'] = criteria.to_dict()
        return self._build(name, data, (ffd.Query,))

    def query_class(self, name: str, fields_: dict = None):
        return self._build_message_class(name, fields_, (ffd.Command,))

    def _build(self, name: str, data: dict, bases: tuple):
        # __pragma__ ('ecom')
        """?
        return make_dataclass(name, data, bases=bases)(**data)
        ?"""
        # __pragma__ ('noecom')

        return self._build_message_class(name, {k: type(v) for k, v in data.items()}, bases)(**data)

    @staticmethod
    def _build_message_class(name: str, fields_: dict, bases: tuple):
        # __pragma__('skip')
        context = None
        if '.' in name:
            context, name = name.split('.')
        ret = ffd.MessageMeta.__new__(ffd.MessageMeta, name, bases, fields_, fields_=fields_, annotations_=fields_)
        if context is not None:
            ret._context = context
        return ret
        # __pragma__('noskip')
