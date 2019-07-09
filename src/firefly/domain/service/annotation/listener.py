from __future__ import annotations

from typing import Union

from .framework_annotation import FrameworkAnnotation


class Listener(FrameworkAnnotation):
    def name(self) -> str:
        return '__ff_listener'

    def __call__(self, event: Union[str, type]):
        return super().__call__(event=event)


listener = Listener()
