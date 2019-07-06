from __future__ import annotations

import firefly.domain as ffd

from .extension import Extension


class Context(Extension):
    @property
    def extensions(self):
        return self._config.get('extensions', {})

    def _load_container(self):
        super()._load_container()
        if self.dispatch(ffd.RegisterContainer(self.name)) is not True:
            raise ffd.FrameworkError('Could not register container for context {}'.format(self.name))
