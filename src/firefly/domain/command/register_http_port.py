from __future__ import annotations

from dataclasses import dataclass
from typing import TypeVar, Type, Union

import firefly.domain as ffd

from .framework_command import FrameworkCommand
from ..entity.messaging.message import Message
from ..service.core.service import Service

M = TypeVar('M', bound=Message)
S = TypeVar('S', bound=Service)


class RegisterHttpPort(FrameworkCommand):
    id_: str = ffd.required()
    device_id: str = ffd.optional()
    parent: str = ffd.optional()
    target: Union[Type[M], Type[S]] = ffd.optional()
    decorated: object = ffd.required()
    endpoint: ffd.HttpEndpoint = ffd.required()
    cors: bool = False
