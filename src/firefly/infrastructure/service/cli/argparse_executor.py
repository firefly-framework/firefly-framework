#  Copyright (c) 2019 JD Williams
#
#  This file is part of Firefly, a Python SOA framework built by JD Williams. Firefly is free software; you can
#  redistribute it and/or modify it under the terms of the GNU General Public License as published by the
#  Free Software Foundation; either version 3 of the License, or (at your option) any later version.
#
#  Firefly is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the
#  implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
#  Public License for more details. You should have received a copy of the GNU Lesser General Public
#  License along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#  You should have received a copy of the GNU General Public License along with Firefly. If not, see
#  <http://www.gnu.org/licenses/>.

import argparse
import os

import inflection
from firefly.domain.meta.build_argument_list import build_argument_list
from firefly.domain.entity.messaging.command import Command
from firefly.domain.entity.messaging.query import Query
from firefly.domain.entity.core.cli_app import CliApp
from firefly.domain.entity.core.cli_argument import CliArgument
from firefly.domain.service.command_line.cli_app_executor import CliAppExecutor
from firefly.domain.service.messaging.message_factory import MessageFactory
from firefly.domain.service.messaging.system_bus import SystemBusAware


class ArgparseExecutor(CliAppExecutor, SystemBusAware):
    _message_factory: MessageFactory = None

    def __init__(self):
        self._app = None
        self._parser = None
        self._tree = {}
        self._message_cache = {}

    def run(self, app: CliApp):
        self._app = app
        params = {}
        if app.description is not None:
            params['description'] = app.description
        self._parser = argparse.ArgumentParser(**params)
        self._initialize()

        args = self._parser.parse_args()

        if args.verbose is True:
            self._logger.set_level_to_info()
        if args.debug is True:
            self._logger.set_level_to_debug()
        # Deprecated. Should use FF_ENVIRONMENT going forward
        os.environ['ENV'] = args.env or 'local'
        os.environ['FF_ENVIRONMENT'] = args.env or 'local'

        try:
            target = args.target
        except AttributeError:
            target = None
        if target is None:
            self._parser.print_help()
            return

        message = self._message_cache[target]
        instance = message(**build_argument_list(vars(args), message))
        if issubclass(message, Command):
            self.invoke(instance)
        elif issubclass(message, Query):
            self.request(instance)

    def _initialize(self):
        self._add_verbosity_arguments(self._parser)
        self._build_node_tree()
        if 'children' not in self._tree:
            return self._configure_single_command_app()
        self._configure_argparse()

    def _build_node_tree(self):
        for endpoint in self._app.endpoints:
            parts = endpoint.command.split(' ')
            if parts[0] == self._app.name:
                parts.pop(0)
            node = self._tree
            if len(parts) > 1:
                for part in parts[:-1]:
                    if 'children' not in node:
                        node['children'] = {}
                    if part not in node['children']:
                        node['children'][part] = {}
                    node = node['children'][part]
            if 'children' not in node:
                node['children'] = {}
            if parts[-1] not in node['children']:
                node['children'][parts[-1]] = {}
            node['children'][parts[-1]]['endpoint'] = endpoint

    def _configure_argparse(self, node: dict = None, parser: argparse.ArgumentParser = None):
        if parser is None:
            parser = self._parser
        if node is None:
            node = self._tree

        if 'endpoint' in node:
            if len(node['endpoint'].arguments):
                for arg in node['endpoint'].arguments:
                    self._add_argument(parser, arg)

        if 'children' in node:
            sp = parser.add_subparsers(help='Commands', dest='target')
            for k, v in node['children'].items():
                p = sp.add_parser(k, help=v['endpoint'].help if 'endpoint' in v else None)
                self._add_verbosity_arguments(p)
                if 'endpoint' in v:
                    self._message_cache[k] = v['endpoint'].message
                self._configure_argparse(v, p)

    @staticmethod
    def _add_argument(parser, arg: CliArgument):
        params = [f'--{inflection.dasherize(arg.name)}'] + [f'-{a}' for a in arg.alias or []]
        kwargs = {
            'default': arg.default,
            'required': arg.required,
            'help': arg.help,
        }
        if arg.help is None and arg.default is not None:
            kwargs['help'] = f'default: {arg.default}'
        if arg.type == bool:
            kwargs['action'] = 'store_true' if not arg.default else 'store_false'
        else:
            kwargs['type'] = arg.type
        try:
            parser.add_argument(*params, **kwargs)
        except argparse.ArgumentError as e:
            if 'conflicting option' not in str(e):
                raise e

    def _configure_single_command_app(self):
        if len(self._app.endpoints):
            for arg in self._app.endpoints[0].arguments:
                self._add_argument(self._parser, arg)

    @staticmethod
    def _add_verbosity_arguments(parser):
        try:
            parser.add_argument('--verbose', '-v', action='store_true', default=False, help='Enable verbose output')
            parser.add_argument('--debug', '-d', action='store_true', default=False, help='Enable debug output')
            parser.add_argument('--env', '-e', action='store', default='local', help='Environment name')
        except argparse.ArgumentError:
            pass
