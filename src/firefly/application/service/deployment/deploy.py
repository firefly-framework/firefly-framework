from __future__ import annotations

import firefly.domain as ffd


@ffd.command_handler('firefly.Deploy')
class Deploy(ffd.ApplicationService):
    def __call__(self, env: str = 'local', **kwargs):
        print(f'Deploying {env}...')
