from __future__ import annotations

import firefly.domain as ffd
import inflection


@ffd.on(ffd.DeploymentCreated)
class ConfigureDeployment(ffd.ApplicationService):
    _context_map: ffd.ContextMap = None

    def __call__(self, deployment: ffd.Deployment):
        self._add_gateways(deployment)
        self._add_message_queues(deployment)

    def _add_gateways(self, deployment: ffd.Deployment):
        gateway = ffd.ApiGateway()

        for context in self._context_map.contexts:
            gateway.endpoints.append(ffd.Endpoint(
                route=f'/{inflection.dasherize(context.name)}',
                method='POST'
            ))

        deployment.api_gateways.append(gateway)

    def _add_message_queues(self, deployment: ffd.Deployment):
        top = ffd.NetworkTopology()

        for context in self._context_map.contexts:
            camel = inflection.camelize(context.name)
            subscribers = self._get_subscribers(context)
            top.forwarders.append(ffd.Forwarder(name=f'{camel}Forwarder', subscribers=subscribers))

        deployment.network_topology = top

    def _get_subscribers(self, context: ffd.Context):
        ret = {}
        for ctx in self._context_map.contexts:
            if ctx.name == context:
                ret[ctx.name] = ctx.queue
                continue

            for service, event_types in ctx.event_listeners.items():
                for event_type in event_types:
                    if isinstance(event_type, str):
                        context_name, _ = event_type.split('.')
                    else:
                        context_name = event_type.get_class_context()
                    if context_name == context.name:
                        ret[context.name] = context.queue

            for service, command_type in ctx.command_handlers.items():
                if isinstance(command_type, str):
                    context_name, _ = command_type.split('.')
                else:
                    context_name = command_type.get_class_context()
                if context_name == context.name:
                    ret[context.name] = context.queue

        return list(ret.values())
