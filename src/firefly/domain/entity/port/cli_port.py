from __future__ import annotations

from dataclasses import asdict

from firefly import domain as ffd

from .port import Port


class CliPort(Port):
    def _transform_input(self, **kwargs) -> ffd.Message:
        if issubclass(self.target, ffd.Command):
            return self.target(**kwargs)

    def _transform_output(self, message: ffd.Message):
        return asdict(message)
