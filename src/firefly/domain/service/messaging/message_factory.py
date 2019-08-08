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
