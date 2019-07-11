from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, TypeVar, Type, Union

import firefly.domain as ffd

from .framework_command import FrameworkCommand
from ..entity.messaging.message import Message

M = TypeVar('M', bound=Message)


@dataclass
class RegisterCliPort(FrameworkCommand):
    id_: str = ffd.required()
    name: str = ffd.required()
    device_id: str = ffd.optional()
    parent: str = ffd.optional()
    target: Union[Type[M], Type[ffd.Service]] = ffd.optional()
    description: str = ffd.optional()
    alias: Dict = ffd.dict_()
    help_: Dict = ffd.dict_()
