from __future__ import annotations

from dataclasses import dataclass

from .framework_command import FrameworkCommand
from ..entity import required


@dataclass
class RegisterPort(FrameworkCommand):
    args: dict = required()
