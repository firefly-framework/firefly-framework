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

from __future__ import annotations

import argparse
import inspect
import logging
from argparse import ArgumentParser
from typing import Type

import firefly.domain as ffd
import inflection


class App:
    def __init__(self, context_map: ffd.ContextMap, system_bus: ffd.SystemBus, message_factory: ffd.MessageFactory,
                 name: str):
        self.name = name
        self._message_factory = message_factory
        self._context_map = context_map
        self._bus = system_bus
        self._ports = []
        self._parser = ArgumentParser()
        self._subparsers = None
        self._message_lookup = {}

        self._initialize()

    def run(self):
        args = self._parser.parse_args()

        if args.verbose is True:
            logging.getLogger().setLevel(logging.INFO)
        if args.debug is True:
            logging.getLogger().setLevel(logging.DEBUG)

        try:
            message = self._message_lookup[args.target]['target']
        except KeyError:
            self._parser.print_usage()
            return

        if isinstance(message, str):
            service = self._context_map.locate_service(message)
            param_target = service.__call__
            _, type_ = service.locate_message(message)
        else:
            param_target = message
            _, type_ = message.locate_message(message)

        result = self._dispatch_message(message, args, param_target, type_)

        handle = ffd.MiddlewareStack(self._message_lookup[args.target]['middleware'])
        result = handle(result)

        print(result)

    def _dispatch_message(self, message, args, target, type_: str):
        if isinstance(message, str):
            message = getattr(self._message_factory, type_)(message, ffd.build_argument_list(args.__dict__, target))
        else:
            message = message(ffd.build_argument_list(args.__dict__, target))

        if type_ == 'command':
            return self._bus.invoke(message)
        if type_ == 'event':
            return self._bus.dispatch(message)
        return self._bus.query(message)

    def _initialize(self):
        self._gather_ports()
        self._add_verbosity_arguments(self._parser)
        self._add_commands()

    def _gather_ports(self):
        for context in self._context_map.contexts:
            for port in context.ports:
                if not hasattr(port, '__ff_cli'):
                    continue
                config = getattr(port, '__ff_cli')
                if config['app_name'] != self.name:
                    continue
                self._ports.append(port)

    def _get_subparsers(self):
        if self._subparsers is None:
            self._subparsers = self._parser.add_subparsers(dest='target')
        return self._subparsers

    @staticmethod
    def _add_verbosity_arguments(parser):
        try:
            parser.add_argument('--verbose', '-v', action='store_true', default=False, help='Enable verbose output')
            parser.add_argument('--debug', '-d', action='store_true', default=False, help='Enable debug output')
        except argparse.ArgumentError:
            pass

    def _add_commands(self, ports: list = None, options: dict = None, parser=None, parent_class=None):
        top_level = False
        if ports is None:
            top_level = True
            ports = self._ports
        if options is None:
            options = {'alias': {}, 'help_': {}, 'middleware': [], 'params': {}}
        if parser is None:
            parser = self._parser

        for port in ports:
            config = getattr(port, '__ff_cli')
            if inspect.isclass(port):
                if not top_level:
                    parser = self._get_subparsers().add_parser(config['name'], help=config['description'])
                options['alias'].update(config['alias'] if config['alias'] is not None else {})
                options['help_'].update(config['help_'] if config['help_'] is not None else {})
                options['middleware'].extend(config['middleware'] if config['middleware'] is not None else [])
                if hasattr(port, '__init__'):
                    options['params'].update(ffd.get_arguments(port.__init__))
                class_ports = []
                for k, v in port.__dict__.items():
                    if hasattr(v, '__ff_cli'):
                        class_ports.append(v)
                self._add_commands(ports=class_ports, options=options, parser=parser, parent_class=port)
            elif inspect.isfunction(port):
                name = inflection.dasherize(config['name'])
                parser = self._get_subparsers().add_parser(name, help=config['description'])
                mw = options['middleware'].copy()
                sig = inspect.signature(port)
                if 'message' in sig.parameters and 'next_' in sig.parameters:
                    instance = parent_class()
                    mw.append(getattr(instance, port.__name__))

                self._message_lookup[name] = {
                    'target': config['target'],
                    'middleware': mw,
                }
                self._add_adapter(port, config, options, parser)

    def _add_adapter(self, func, config: dict, options: dict, parser):
        message = config['target']
        params = None
        if isinstance(message, str):
            service = self._context_map.locate_service(message)
            if service is not None:
                params = ffd.get_arguments(service.__call__)
        else:
            params = ffd.get_arguments(message)

        if params is None:
            raise ffd.FrameworkError(f'Could not locate service {message}')

        options['params'].update(params)
        options['alias'].update(config['alias'] if config['alias'] is not None else {})
        options['help_'].update(config['help_'] if config['help_'] is not None else {})
        options['middleware'].extend(config['middleware'] if config['middleware'] is not None else [])
        for name, config in options['params'].items():
            args = [f'--{inflection.dasherize(name)}']
            if name in options['alias']:
                args.append(f'-{options["alias"][name]}')

            kwargs = {
                'default': config['default'],
                'required': config['default'] is inspect.Parameter.empty,
                'help': options['help_'][name] if name in options['help_'] else None,
            }

            if config['type'] == bool:
                kwargs['action'] = 'store_true' if not config['default'] else 'store_false'
            else:
                kwargs['type'] = config['type']

            parser.add_argument(*args, **kwargs)
