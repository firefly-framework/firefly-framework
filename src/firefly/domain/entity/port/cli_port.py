from __future__ import annotations

import dataclasses
from dataclasses import asdict

from firefly import domain as ffd

from .port import Port


class CliPort(Port):
    def _transform_input(self, **kwargs) -> ffd.Message:
        message = self.target(**self._drop_extra_args(kwargs))
        message.headers['origin'] = 'cli'
        return message

    def _transform_output(self, message: ffd.Message):
        if dataclasses.is_dataclass(message):
            return asdict(message)
        return message

    def _drop_extra_args(self, kwargs):
        args = {}
        fields = [f.name for f in dataclasses.fields(self.target)]
        for k, v in kwargs.items():
            if k in fields:
                args[k] = v

        return args
