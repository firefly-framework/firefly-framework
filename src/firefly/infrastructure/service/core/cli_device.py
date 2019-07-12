from __future__ import annotations

import argparse
import inspect
import logging
from dataclasses import asdict
from typing import Optional

import firefly.domain as ffd
import inflection


class CliDevice(ffd.Device):
    def __init__(self, device_id: str = None):
        super().__init__()
        
        self._device_id = device_id
        self._parser = argparse.ArgumentParser()
        self._ports = []

    def run(self):
        self._configure_arguments(self._parser)
        args = self._parser.parse_args()
        if args.verbose is True:
            logging.getLogger().setLevel(logging.INFO)
        if args.debug is True:
            logging.getLogger().setLevel(logging.DEBUG)

        if len(self._ports) == 0:
            return

        port: Optional[ffd.CliPort] = None
        if len(self._ports) == 1:
            port = self._ports[0]
        elif hasattr(args, 'service'):
            found = False
            for port in self._ports:
                if port.name == args.service:
                    found = True
                    break
            if not found:
                self._parser.print_help()
                exit()

        args = args.__dict__
        try:
            del args['service']
        except KeyError:
            pass

        if port is not None and port.target is not None:
            return port.handle(**args)
        else:
            self._parser.print_help()

    def register_port(self, command: ffd.RegisterCliPort):
        target = command.target
        if target is not None and issubclass(target, ffd.Service):
            target = target.get_message()
        port = ffd.CliPort(target, asdict(command))
        port._system_bus = self._system_bus
        self._ports.append(port)

    def _initialize_port(self, port: ffd.CliPort, args: dict):
        parent = self._get_parent(port)
        parent_class = self._instantiate_class(parent.decorated, args)

        ancestor = self._get_parent(parent)
        while True:
            if ancestor is None:
                break
            self._instantiate_class(ancestor.decorated, args)
            ancestor = self._get_parent(ancestor)

        if 'next_' in inspect.signature(getattr(parent_class, port.decorated.__name__)).parameters:
            return getattr(parent_class, port.decorated.__name__)

        return None

    @staticmethod
    def _instantiate_class(cls, args):
        params = ffd.get_arguments(cls.__init__) if hasattr(cls, '__init__') else {}
        kwargs = {}
        for k, v in params.items():
            if k in args:
                kwargs[k] = args[k]
        return cls(**kwargs)

    def _gather_params(self, port: ffd.CliPort) -> dict:
        ret = {
            'help': port.help_ or {},
            'alias': port.alias or {},
            'params': {},
        }
        if port.target is not None:
            try:
                ret['params'].update(port.target.get_arguments())
            except AttributeError:
                pass

        while port.parent is not None:
            port = self._get_parent(port)
            if port.help_ is not None:
                ret['help'].update(port.help_)
            if port.alias is not None:
                ret['alias'].update(port.alias)

        return ret

    def _get_top_level_ports(self):
        containers = []
        for port in self._ports:
            if port.device_id is not None and port.device_id == self._device_id:
                containers.append(port)

        ret = []
        for port in self._ports:
            for container in containers:
                if port.parent == container.id_:
                    ret.append(port)

        return ret

    def _get_parent(self, port: ffd.CliPort):
        for p in self._ports:
            if p.id_ == port.parent:
                return p
        return None

    @staticmethod
    def _add_verbosity_arguments(parser):
        try:
            parser.add_argument('--verbose', '-v', action='store_true', default=False, help='Enable verbose output')
            parser.add_argument('--debug', '-d', action='store_true', default=False, help='Enable debug output')
        except argparse.ArgumentError:
            pass

    def _get_children(self, id_):
        ret = []
        for port in self._ports:
            if port.parent == id_:
                ret.append(port)
        return ret

    def _configure_arguments(self, parser, parent: ffd.CliPort = None):
        if parent is None:
            ports = self._get_top_level_ports()
        else:
            ports = self._get_children(parent.id_)
            if len(ports) == 0:
                return

        self._add_verbosity_arguments(parser)

        subparsers = None
        only_one_service = len(ports) == 1 and ports[0].parent is None
        if not only_one_service:
            subparsers = parser.add_subparsers(dest='service')

        for port in ports:
            if not only_one_service:
                parser = subparsers.add_parser(port.name, help=port.description)
                self._add_verbosity_arguments(parser)

            params = self._gather_params(port)
            alias = params['alias']
            help_ = params['help']

            for name, options in params['params'].items():
                args = [f'--{name.replace("_", "-")}']
                if name in alias:
                    args.append(f'-{alias[name]}')

                kwargs = {
                    'default': options['default'],
                    'required': options['default'] is inspect.Parameter.empty,
                    'help': help_[name] if name in help_ else None,
                }

                if options['type'] == bool:
                    kwargs['action'] = 'store_true' if not options['default'] else 'store_false'
                else:
                    kwargs['type'] = options['type']

                parser.add_argument(*args, **kwargs)

            self._configure_arguments(parser, port)
