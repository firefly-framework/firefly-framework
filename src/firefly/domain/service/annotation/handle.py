from __future__ import annotations

from typing import Union

from .framework_annotation import FrameworkAnnotation


class Handle(FrameworkAnnotation):
    def name(self) -> str:
        return '__ff_handler'

    def __call__(self, command: Union[str, type]):
        return super().__call__(command=command)


handle = Handle()
