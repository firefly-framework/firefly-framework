from typing import Callable, Optional

import firefly.application as ffa
from firefly.domain import cli, query_handler, Middleware, Message, Kernel
from firefly.infrastructure import CliDevice
from terminaltables import SingleTable


def main():
    Kernel(CliDevice('firefly')).run()


@query_handler()
class CliOutput(Middleware):
    def __call__(self, message: Message, next_: Callable, **kwargs) -> Optional[dict]:
        response = next_(message)

        if message.headers.get('origin') != 'cli':
            return response

        if isinstance(response, dict):
            for title, data in response.items():
                response[title].insert(0, ('Name', 'Type'))
                print(SingleTable(data, title).table)
        elif isinstance(response, list):
            response.insert(0, ('Name', 'Type'))
            print(SingleTable(response).table)

        return response


@cli(
    device_id='firefly',
    description='Firefly command line utilities',
)
class FireflyCli:
    @cli(description='View information about the internals of your application')
    class List:

        @cli(
            target=ffa.GetRegisteredContainerServices,
            description='Print registered services',
            alias={
                'flatten': 'f',
                'no_extensions': 'ne',
                'provider': 'p'
            },
            help_={
                'flatten': 'Include services in registered sub-containers',
                'no_extensions': 'Do not print containers for extensions',
                'provider': 'Only print the container for the given provider'
            }
        )
        def containers(self):
            pass

    @cli(description='Firefly HTTP server')
    class Http:

        @cli(
            target=ffa.DeployHttp,
            description='Deploy services to the HTTP server',
            alias={
                'port': 'p',
            }
        )
        def deploy(self):
            pass
