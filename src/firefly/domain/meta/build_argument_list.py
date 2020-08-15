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
import keyword
import typing
from datetime import datetime

import firefly.domain as ffd

# __pragma__('skip')
from dataclasses import is_dataclass, fields
from abc import ABC
# __pragma__('noskip')
# __pragma__ ('ecom')
from dateparser import parse

"""?
from firefly.presentation.web.polyfills import is_dataclass, fields
?"""
# __pragma__ ('noecom')


keyword_list = keyword.kwlist
keyword_list.append('id')


def _fix_keywords(params: dict):
    if not isinstance(params, dict):
        return params

    for k, v in params.copy().items():
        if k in keyword_list:
            params[f'{k}_'] = v
    return params


def build_argument_list(params: dict, obj: typing.Union[typing.Callable, type]):
    args = {}
    field_dict = {}
    is_dc = False
    params = _fix_keywords(params)

    if is_dataclass(obj):
        is_dc = True
        field_dict = {}
        # noinspection PyDataclass
        for field_ in fields(obj):
            field_dict[field_.name] = field_
        sig = inspect.signature(obj.__init__)
        types = typing.get_type_hints(obj)
    elif isinstance(obj, ffd.MetaAware):
        sig = inspect.signature(obj.__call__)
        types = typing.get_type_hints(obj.__call__)
    elif isinstance(obj, type):
        sig = inspect.signature(obj.__init__)
        types = typing.get_type_hints(obj.__init__)
    else:
        sig = inspect.signature(obj)
        try:
            types = typing.get_type_hints(obj)
        except NameError:
            types = obj.__annotations__

    for param in sig.parameters.values():
        if param.kind == inspect.Parameter.VAR_KEYWORD:
            return params

    for name, param in sig.parameters.items():
        if name == 'self' or param.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
            continue

        required = False
        if is_dc:
            required = field_dict[name].metadata.get('required', False) is True
            try:
                d = field_dict[name].default_factory()
                if not isinstance(d, ffd.Empty):
                    required = False
            except (AttributeError, TypeError):
                pass
        elif param.default is not None:
            required = True

        type_ = types[name] if name in types else None
        if type_ is datetime and name in params and isinstance(params[name], str):
            params[name] = parse(params[name]).replace(tzinfo=None)

        if isinstance(type_, type) and issubclass(type_, ffd.ValueObject):
            if name in params and isinstance(params[name], type_):
                args[name] = params[name]
                continue

            try:
                nested = False
                if name in params and isinstance(params[name], dict):
                    e = _generate_model(params[name], type_)
                    nested = True
                else:
                    e = _generate_model(params, type_)
            except ffd.MissingArgument:
                if required is False:
                    continue
                raise
            # TODO use factories where appropriate
            args[name] = e
            if nested:
                del params[name]
            else:
                for key in e.to_dict().keys():
                    if (not hasattr(type_, 'id_name') or key != type_.id_name()) and key in params:
                        del params[key]
                        if key in args:
                            del args[key]
        elif isinstance(type_, type(typing.List)) and issubclass(type_.__args__[0], ffd.ValueObject):
            args[name] = []
            if isinstance(params, dict) and name in params:
                for d in params[name]:
                    if isinstance(d, type_.__args__[0]):
                        args[name].append(d)
                    else:
                        try:
                            e = _generate_model(d, type_.__args__[0])
                        except ffd.MissingArgument:
                            if required is False:
                                continue
                            raise
                        args[name].append(e)
                        if e is False and required is True:
                            raise ffd.MissingArgument()

        elif isinstance(type_, type(typing.Dict)) and len(type_.__args__) == 2 and \
                issubclass(type_.__args__[1], ffd.ValueObject):
            args[name] = {}
            if isinstance(params, dict) and name in params:
                for k, d in params[name].items():
                    try:
                        entity_args = build_argument_list(d, type_.__args__[1])
                    except ffd.MissingArgument:
                        if required is False:
                            continue
                        raise
                    args[name][k] = type_.__args__[1](**entity_args)
        elif isinstance(params, dict) and name in params:
            args[name] = params[name]
        elif name.endswith('_') and name.rstrip('_') in params:
            args[name] = params[name.rstrip('_')]
        elif required is True:
            raise ffd.MissingArgument(f'Argument: {name} is required')

    return args


def _generate_model(args: dict, model_type: type, strict: bool = False):
    subclasses = model_type.__subclasses__()
    if len(subclasses):
        for subclass in subclasses:
            try:
                return _generate_model(args, subclass, strict=True)
            except RuntimeError:
                continue

    entity_args = build_argument_list(args, model_type)
    if strict:
        for k in args.keys():
            if k not in entity_args:
                raise RuntimeError()

    return model_type(**entity_args)
