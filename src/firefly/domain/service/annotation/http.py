from __future__ import annotations

from .framework_annotation import FrameworkAnnotation


class Http(FrameworkAnnotation):
    def name(self) -> str:
        return '__ff_port'

    def __call__(self, path: str = None, method: str = 'get', for_: type = None, cors: bool = False):
        kwargs = locals()
        del kwargs['self']
        return super().__call__(port_type='http', **kwargs)


http = Http()
