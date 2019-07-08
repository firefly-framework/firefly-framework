from __future__ import annotations

from .framework_annotation import FrameworkAnnotation


class Cli(FrameworkAnnotation):
    def name(self) -> str:
        return '__ff_port'

    def __call__(self, name: str = None, description: str = None, for_: object = None, alias: dict = None,
                 help_: dict = None, app_id: str = None, params: dict = None):
        kwargs = locals()
        del kwargs['self']
        return super().__call__(port_type='cli', **kwargs)


cli = Cli()
