from __future__ import annotations

from dataclasses import MISSING, dataclass

from .framework_command import FrameworkCommand


@dataclass
class RegisterPort(FrameworkCommand):
    args: dict = MISSING
