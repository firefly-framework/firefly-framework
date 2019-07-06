from __future__ import annotations

import firefly.domain as ffd
from .framework_command import FrameworkCommand


class RegisterPresentationMiddleware(FrameworkCommand):
    def __init__(self, cls: ffd.Middleware):
        super().__init__(body=cls)
