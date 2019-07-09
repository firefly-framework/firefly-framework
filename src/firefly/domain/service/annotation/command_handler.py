from __future__ import annotations

from typing import Union

from .framework_annotation import FrameworkAnnotation


class CommandHandler(FrameworkAnnotation):
    def name(self) -> str:
        return '__ff_command_handler'

    def __call__(self, command: Union[str, type, None] = None):
        return super().__call__(command=command)


command_handler = CommandHandler()
