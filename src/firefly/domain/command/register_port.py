from __future__ import annotations

from .framework_command import FrameworkCommand


class RegisterPort(FrameworkCommand):
    def __init__(self, **kwargs):
        super().__init__(body=kwargs)
