from __future__ import annotations

import argparse
import inspect
import logging
from typing import Optional

import firefly.domain as ffd
import inflection


class CliDevice(ffd.Device):
    def __init__(self, app_id: str = None):
        super().__init__()
        
        self._app_id = app_id
        self._parser = argparse.ArgumentParser()

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

        if port is not None and port.service is not None:
            middleware = self._initialize_port(port, args)
            if middleware is not None:
                self._bus.add(middleware)
            request = ffd.Request(headers=args)
            request.header('origin', 'cli')
            request.service = port.service
            return self.dispatch(request)
        else:
            self._parser.print_help()

    def register_port(self, **kwargs):
        if kwargs['port_type'] != 'cli':
            return

        del kwargs['port_type']
        self._build_ports(kwargs)

    def _build_ports(self, args: dict, parent: ffd.CliPort = None):
        if 'port_type' in args:
            del args['port_type']
        if '__class__' in args:
            del args['__class__']

        port = ffd.CliPort(**args)
        if port.name is None:
            port.name = inflection.dasherize(port.target.__name__).lower()

        if parent is not None:
            port.extend(parent)

        if inspect.isclass(port.target):
            for k, v in port.target.__dict__.items():
                if hasattr(v, '__ff_port'):
                    for kwargs in getattr(v, '__ff_port'):
                        kwargs['target'] = v
                        self._build_ports(kwargs, port)

        self._ports.append(port)

    def _initialize_port(self, port: ffd.CliPort, args: dict):
        parent = port.parent
        parent_class = self._instantiate_class(parent.target, args)

        ancestor = parent.parent
        while True:
            if ancestor is None:
                break
            self._instantiate_class(ancestor.target, args)
            ancestor = ancestor.parent

        if 'next_' in inspect.signature(getattr(parent_class, port.target.__name__)).parameters:
            return getattr(parent_class, port.target.__name__)

        return None

    @staticmethod
    def _instantiate_class(cls, args):
        params = ffd.get_arguments(cls.__init__) if hasattr(cls, '__init__') else {}
        kwargs = {}
        for k, v in params.items():
            if k in args:
                kwargs[k] = args[k]
        return cls(**kwargs)

    @staticmethod
    def _gather_params(port: ffd.CliPort) -> dict:
        ret = {
            'help': port.help or {},
            'alias': port.alias or {},
            'params': {},
        }
        if port.service is not None:
            try:
                ret['params'].update(port.service.get_arguments())
            except AttributeError:
                pass
        if port.params is not None:
            ret['params'].update(port.params)

        while port.parent is not None:
            port = port.parent
            if port.params is not None:
                ret['params'].update(port.params)
            if port.help is not None:
                ret['help'].update(port.help)
            if port.alias is not None:
                ret['alias'].update(port.alias)

        return ret

    def _get_top_level_ports(self):
        containers = []
        for port in self._ports:
            if not isinstance(port, ffd.CliPort):
                continue
            if port.app_id is not None and port.app_id == self._app_id:
                containers.append(port)

        ret = []
        for container in containers:
            ret.extend(container.children)

        return ret

    @staticmethod
    def _add_verbosity_arguments(parser):
        try:
            parser.add_argument('--verbose', '-v', action='store_true', default=False, help='Enable verbose output')
            parser.add_argument('--debug', '-d', action='store_true', default=False, help='Enable debug output')
        except argparse.ArgumentError:
            pass

    def _configure_arguments(self, parser, parent: ffd.CliPort = None):
        if parent is None:
            ports = self._get_top_level_ports()
        else:
            ports = parent.children
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
