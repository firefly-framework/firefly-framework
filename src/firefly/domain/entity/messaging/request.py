from __future__ import annotations

from .message import Message


class Request(Message):
    @property
    def service(self):
        return self.header('service')

    @service.setter
    def service(self, value):
        self.header('service', value)
