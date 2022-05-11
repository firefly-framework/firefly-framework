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

import inspect
import os

import firefly.domain as ffd
from firefly.domain.entity.core.cli import CliArgument, CliEndpoint
import firefly.domain.constants as const


class Cli:
    def __call__(self, command: str, app: str = None, description: str = None, target=None,
                 alias: dict = None, help_: str = None, args_help: dict = None):
        def cli_wrapper(cls):
            arguments = []

            if inspect.isfunction(cls):
                args = ffd.get_arguments(cls, none_type_unions=False)
            else:
                args = ffd.get_arguments(cls.__call__, none_type_unions=False)

            for name, arg in args.items():
                arguments.append(CliArgument(
                    name=name,
                    type=arg['type'],
                    default=arg['default'] if arg['default'] is not inspect.Parameter.empty else None,
                    required=arg['default'] is inspect.Parameter.empty,
                    help=args_help[name] if isinstance(args_help, dict) and name in args_help else None,
                    alias=alias[name] if isinstance(alias, dict) and name in alias else None
                ))

            endpoint = CliEndpoint(
                app=app if app is not None else command.split(' ')[0],
                command=command,
                description=description,
                help=help_,
                arguments=arguments,
                service=cls
            )

            if hasattr(cls, const.CLI_ENDPOINTS):
                getattr(cls, const.CLI_ENDPOINTS).append(endpoint)
            else:
                setattr(cls, const.CLI_ENDPOINTS, [endpoint])

            return cls

        return cli_wrapper


cli = Cli()
