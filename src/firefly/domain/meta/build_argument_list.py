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
from dataclasses import is_dataclass, fields, MISSING
from datetime import datetime, date

import firefly.domain as ffd
from dateparser import parse
from firefly.domain.meta.firefly_type import FireflyType
from firefly.domain.utils import is_type_hint

keyword_list = keyword.kwlist
keyword_list.append('id')


def _fix_keywords(params: dict):
    if not isinstance(params, dict):
        return params

    for k, v in params.copy().items():
        if k in keyword_list:
            params[f'{k}_'] = v
    return params


class Void:
    pass


void = Void()


def _handle_type_hint(params: typing.Any, t: type, key: str = None, required: bool = False):
    ret = {}

    origin = typing.get_origin(t)
    args = typing.get_args(t)

    if origin is typing.List:
        if key not in params:
            if required:
                raise ffd.MissingArgument(f'Missing argument {key} for type {t}')
            return []

        if is_type_hint(args[0]):
            if key is not None:
                ret[key] = list(map(lambda a: _handle_type_hint(a, args[0]), params[key]))
            else:
                ret = list(map(lambda a: _handle_type_hint(a, args[0]), params[key]))
        elif inspect.isclass(args[0]) and issubclass(args[0], ffd.ValueObject):
            try:
                if key is not None:
                    ret[key] = []
                    for v in params[key]:
                        parameter = args[0].from_dict(v)
                        if parameter is not None:
                            ret[key].append(parameter)
                    if len(ret[key]) == 0:
                        del ret[key]
                else:
                    ret = list(map(lambda a: args[0].from_dict(a), params[key]))
            except TypeError:
                return
        else:
            ret[key] = params[key]

    elif origin is typing.Dict:
        if key not in params:
            if required:
                raise ffd.MissingArgument()
            return {}

        if is_type_hint(args[1]):
            ret[key] = {k: _handle_type_hint(v, args[1]) for k, v in params[key].items()}
        elif inspect.isclass(args[1]) and issubclass(args[1], ffd.ValueObject):
            ret[key] = {k: args[1].from_dict(v) for k, v in params[key].items()}
        else:
            ret[key] = params[key]

    elif origin is typing.Union:
        for arg in args:
            r = _handle_type_hint(params, arg, key, required)
            if r is not void:
                if key is not None:
                    ret[key] = r
                else:
                    ret = r
                break

    else:
        if inspect.isclass(t) and issubclass(t, ffd.ValueObject):
            if key in params:
                return t.from_dict(params[key])
            else:
                return t.from_dict(params)

        try:
            if key is not None:
                if key in params:
                    val = _check_special_types(params[key], t)
                    if val is not None:
                        return val

                    try:
                        if t(params[key]) == params[key]:
                            return params[key]
                    except ValueError:
                        pass
                    if params[key] is None:
                        return None
                elif str(t) == "<class 'NoneType'>":
                    return None

            elif key is None and t(params) == params:
                return params
        except (TypeError, KeyError):
            pass

    if ret == {}:
        return void

    return ret


def _check_special_types(value: typing.Any, type_: type):
    if type_ is datetime and isinstance(value, str):
        return parse(value).replace(tzinfo=None)
    elif type_ is date and isinstance(value, str):
        return parse(value).replace(tzinfo=None).date()


def build_argument_list(params: dict, obj: typing.Union[typing.Callable, type], strict: bool = True,
                        include_none_parameters: bool = False):
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
    elif inspect.isclass(obj) and hasattr(obj, '__call__'):
        sig = inspect.signature(obj.__call__)
        types = typing.get_type_hints(obj.__call__)
    elif not inspect.isclass(obj) and isinstance(obj, FireflyType):
        sig = inspect.signature(obj.__class__.__call__)
        types = typing.get_type_hints(obj.__class__.__call__)
    elif isinstance(obj, type):
        sig = inspect.signature(obj.__init__)
        types = typing.get_type_hints(obj.__init__)
    else:
        sig = inspect.signature(obj)
        try:
            types = typing.get_type_hints(obj)
        except NameError:
            types = obj.__annotations__

    has_kwargs = False
    for param in sig.parameters.values():
        if param.kind == inspect.Parameter.VAR_KEYWORD:
            has_kwargs = True

    for name, param in sig.parameters.items():
        if name == 'self' or param.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
            continue

        required = False
        if is_dc:
            required = field_dict[name].metadata.get('required', False) is True
            try:
                d = field_dict[name].default_factory()
                if d is not MISSING:
                    required = False
            except (AttributeError, TypeError):
                pass
        elif param.default == inspect.Parameter.empty:
            required = True

        type_ = types[name] if name in types else None
        if params and name in params:
            val = _check_special_types(params[name], type_)
            if val is not None:
                params[name] = val

        if isinstance(type_, type) and issubclass(type_, ffd.ValueObject):
            if params is None:
                if required is False:
                    continue
                raise ffd.MissingArgument(name)

            if name in params and isinstance(params[name], type_):
                args[name] = params[name]
                continue

            nested = False
            if name in params and isinstance(params[name], dict):
                args[name] = type_.from_dict(params[name])
                nested = True
            elif isinstance(params, dict):
                args[name] = type_.from_dict(params)

            if nested:
                del params[name]

        elif is_type_hint(type_):
            if type_ is typing.Any:
                if name in params:
                    args[name] = params[name]
            else:
                if name in params:
                    parameter_args = _handle_type_hint({name: params[name]}, type_, key=name, required=required)
                elif isinstance(params, dict):
                    parameter_args = _handle_type_hint(copy_params(params, sig), type_, key=name, required=required)
                if parameter_args and not isinstance(parameter_args, Void):
                    args.update(parameter_args)

        elif isinstance(params, dict) and name in params:
            try:
                if params[name] is None:
                    if not is_dc or include_none_parameters is True:
                        args[name] = None
                elif isinstance(params[name], bytes):
                    args[name] = params[name]
                else:
                    try:
                        args[name] = type_(params[name])
                    except OverflowError:
                        args[name] = params[name]
            except TypeError:
                args[name] = params[name]
        elif name.endswith('_') and name.rstrip('_') in params:
            try:
                sname = name.rstrip('_')
                if params[sname] is None:
                    if not is_dc or include_none_parameters is True:
                        args[name] = None
                elif isinstance(params[sname], bytes):
                    args[name] = params[sname]
                else:
                    try:
                        args[name] = type_(params[sname])
                    except OverflowError:
                        args[name] = params[name]
            except TypeError:
                args[name] = params[name.rstrip('_')]
        elif required is True and strict:
            raise ffd.MissingArgument(f'Argument: {name} is required for object {obj}')

    if has_kwargs:
        for k, v in params.items():
            if k not in args:
                args[k] = v

    return args


def copy_params(params: dict, sig: inspect.Signature):
    params_copy = params.copy()
    for n in sig.parameters.keys():
        if n in params_copy:
            del params_copy[n]
    return params_copy
