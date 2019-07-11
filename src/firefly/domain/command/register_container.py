from __future__ import annotations

from dataclasses import dataclass

from .framework_command import FrameworkCommand


@dataclass
class RegisterContainer(FrameworkCommand):
    context_name: str = None
