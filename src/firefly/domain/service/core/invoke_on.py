from __future__ import annotations

from dataclasses import asdict

import firefly.domain as ffd

from ..core.application_service import ApplicationService


class InvokeOn(ApplicationService):
    _message_factory: ffd.MessageFactory = None

    def __init__(self, command_name: str):
        self._command_name = command_name

    def __call__(self, **kwargs):
        return self.invoke(self._message_factory.command(self._command_name, asdict(kwargs['_message'])))
