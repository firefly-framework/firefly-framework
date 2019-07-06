from __future__ import annotations

from .framework_annotation import FrameworkAnnotation


class Middleware(FrameworkAnnotation):
    def name(self) -> str:
        return '__ff_middleware'

    def __call__(self):
        return super().__call__()


middleware = Middleware()
