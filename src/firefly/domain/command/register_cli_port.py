from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, TypeVar, Type, Union

import firefly.domain as ffd

from .framework_command import FrameworkCommand
from ..entity.messaging.message import Message
from ..service.core.service import Service

M = TypeVar('M', bound=Message)
S = TypeVar('S', bound=Service)


@dataclass
class RegisterCliPort(FrameworkCommand):
    id_: str = ffd.required()
    name: str = ffd.required()
    device_id: str = ffd.optional()
    parent: str = ffd.optional()
    target: Union[Type[M], Type[S]] = ffd.optional()
    description: str = ffd.optional()
    alias: Dict = ffd.dict_()
    help_: Dict = ffd.dict_()
    decorated: object = ffd.required()
    params: Dict = ffd.dict_()
