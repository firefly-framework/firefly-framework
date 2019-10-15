from __future__ import annotations

import firefly.domain as ffd


@ffd.command_handler('firefly.Deploy')
class Deploy(ffd.ApplicationService):
    _config: ffd.Configuration = None
    _agent_factory: ffd.AgentFactory = None

    def __call__(self, env: str = 'local', **kwargs):
        config = self._config.environments.get(env, {})
        provider = config.get('provider', 'default')
        deployment = ffd.Deployment(environment=env, provider=provider)
        self.dispatch(ffd.DeploymentCreated(deployment=deployment))
        self.dispatch(ffd.DeploymentInitialized(deployment=deployment))

        agent = self._agent_factory(provider)
        self.dispatch(ffd.DeploymentStarting(deployment=deployment))
        agent.handle(deployment, **kwargs)
        self.dispatch(ffd.DeploymentComplete(deployment=deployment))
