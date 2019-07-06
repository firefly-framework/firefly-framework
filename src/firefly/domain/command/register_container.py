from __future__ import annotations

from .framework_command import FrameworkCommand


class RegisterContainer(FrameworkCommand):
    def __init__(self, context_name: str):
        super().__init__(body=context_name)
