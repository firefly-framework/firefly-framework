from typing import Callable, Optional

from firefly.infrastructure.cli.app import App

import firefly.domain as ffd
from terminaltables import SingleTable


def main():
    from firefly.application import Container
    container = Container()
    container.kernel.boot()
    app = App(container.context_map, container.system_bus, container.message_factory, 'firefly')
    app.run()


class CliOutput(ffd.Middleware):
    def __call__(self, message: ffd.Message, next_: Callable, **kwargs) -> Optional[dict]:
        print('CliOutput called...')
        response = next_(message)

        if isinstance(response, dict):
            for title, data in response.items():
                response[title].insert(0, ('Name', 'Type'))
                print(SingleTable(data, title).table)
        elif isinstance(response, list):
            response.insert(0, ('Name', 'Type'))
            print(SingleTable(response).table)

        return response


@ffd.cli(
    app_name='firefly',
    description='Firefly command line utilities',
    middleware=[CliOutput()]
)
class FireflyCli:

    @ffd.cli(
        target='firefly.Deploy',
        alias={
            'env': 'e',
        },
        help_={
            'env': 'The environment to deploy'
        }
    )
    def deploy(self, message: ffd.Message, next_: Callable, **kwargs):
        print('Deploy called...')
        return next_(message)

    # @ffd.cli(description='View information about the internals of your application')
    # class List:
    #
    #     @ffd.cli(
    #         target=ffa.GetRegisteredContainerServices,
    #         description='Print registered services',
    #         alias={
    #             'flatten': 'f',
    #             'no_extensions': 'ne',
    #             'provider': 'p'
    #         },
    #         help_={
    #             'flatten': 'Include services in registered sub-containers',
    #             'no_extensions': 'Do not print containers for extensions',
    #             'provider': 'Only print the container for the given provider'
    #         }
    #     )
    #     def containers(self):
    #         pass

    # @ffd.cli(description='Firefly HTTP server')
    # class Http:
    #
    #     @ffd.cli(
    #         target=ffa.DeployHttp,
    #         description='Deploy services to the HTTP server',
    #         alias={
    #             'port': 'p',
    #         }
    #     )
    #     def deploy(self):
    #         pass
