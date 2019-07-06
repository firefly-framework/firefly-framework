from __future__ import annotations

import logging

import firefly.domain as ffd


class PythonLogger(ffd.Logger):
    def __init__(self):
        self.log = logging

    def debug(self, message: str, *args, **kwargs):
        self.log.debug(message, *args, **kwargs)

    def info(self, message: str, *args, **kwargs):
        self.log.info(message, *args, **kwargs)

    def warning(self, message: str, *args, **kwargs):
        self.log.warning(message, *args, **kwargs)

    def error(self, message: str, *args, **kwargs):
        self.log.error(message, *args, **kwargs)
