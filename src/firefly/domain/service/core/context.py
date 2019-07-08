from __future__ import annotations

from .extension import Extension


class Context(Extension):
    @property
    def extensions(self):
        return self.config.get('extensions', {})
