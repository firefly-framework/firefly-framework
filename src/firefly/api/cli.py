from typing import Callable, Optional

import firefly.application as ffa
from firefly.domain import cli, middleware, Middleware, Message, Kernel
from firefly.domain.service.core.CliHub import CliHub
from terminaltables import SingleTable


def main():
    Kernel(CliHub('firefly')).run()


@middleware()
class CliOutput(Middleware):
    def __call__(self, message: Message, next_: Callable, **kwargs) -> Optional[dict]:
        response = next_(message)

        output = response.body()
        if isinstance(output, dict):
            for title, data in output.items():
                output[title].insert(0, ('Name', 'Type'))
                print(SingleTable(data, title).table)
        elif isinstance(output, list):
            output.insert(0, ('Name', 'Type'))
            print(SingleTable(output).table)

        return response


@cli(
    app_id='firefly',
    description='Firefly command line utilities',
)
class FireflyCli:
    @cli(description='View information about the internals of your application')
    class List:

        @cli(
            for_=ffa.GetRegisteredContainerServices,
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
