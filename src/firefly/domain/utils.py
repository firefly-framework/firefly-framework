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

import importlib
import inspect
import sys
import typing
from dataclasses import dataclass
from time import sleep

import firefly as ff


def retry(cb, valid_cb=None, wait: int = 1, backoff: bool = True, retries: int = 5, catch=Exception, should_retry=None):
    while retries > 0:
        try:
            ret = cb()
            if valid_cb is not None and not valid_cb(ret):
                raise RuntimeError('valid_cb is false-y for return value')
            return ret
        except catch as e:
            if should_retry is not None and not should_retry(e):
                raise e
            retries -= 1
            if retries <= 0:
                raise e
            sleep(wait)
            if backoff:
                wait *= 2


def load_class(fqn: str):
    pieces = fqn.split('.')
    module_name = '.'.join(pieces[0:-1])
    class_ = pieces[-1]

    if module_name not in sys.modules:
        try:
            module = importlib.import_module(module_name)
            return getattr(module, class_)
        except (ImportError, AttributeError):
            return None

    try:
        return getattr(sys.modules[module_name], class_)
    except AttributeError:
        return None


def generate_dc(base: type, _cls, **kwargs):
    if 'eq' not in kwargs:
        kwargs['eq'] = False
    if 'repr' not in kwargs:
        kwargs['repr'] = False

    def wrapper(cls):
        dc = dataclass(cls, **kwargs)
        if issubclass(dc, base):
            return dc

        class Wrapper(dc, base):
            pass
        Wrapper.__name__ = cls.__name__

        return dataclass(Wrapper, **kwargs)

    if _cls is None:
        return wrapper

    return wrapper(_cls)


# Python 3.7
if sys.version_info[1] == 7:
    def is_type_hint(obj):
        return isinstance(obj, (typing._GenericAlias, typing._SpecialForm))

    def get_origin(obj):
        try:
            ret = obj.__origin__
            if hasattr(ret, '__name__') and ret.__name__ in typing._normalize_alias:
                return getattr(typing, typing._normalize_alias[ret.__name__])
            return ret
        except AttributeError:
            return None

    def get_args(obj):
        if not is_type_hint(obj):
            return None
        try:
            return obj.__args__
        except AttributeError:
            return None


def can_be_type(x, t):
    if inspect.isclass(x):
        return issubclass(x, t)

    if is_type_hint(x):
        if get_origin(x) is typing.Union:
            for arg in get_args(x):
                if can_be_type(arg, t):
                    return True

    return False


class ValueMeta(type):
    def __new__(mcs, name, bases, dct, **kwargs):
        ret = type.__new__(mcs, name, bases, dct)
        return dataclass(ret, frozen=True)


def has_meta(cls):
    return hasattr(cls, '__FIREFLY__')


def check_for_meta(cls):
    if not has_meta(cls):
        cls.__FIREFLY__ = type.__new__(type, f'{cls.__name__}Meta', (ff.MetaAware,), {})


def add_endpoint(cls, endpoint: ff.Endpoint):
    check_for_meta(cls)
    cls.__FIREFLY__.add_endpoint(endpoint)


def add_event(cls, event: ff.TypeOfEvent):
    check_for_meta(cls)
    cls.__FIREFLY__.add_event(event)


def set_command(cls, command: ff.TypeOfCommand):
    check_for_meta(cls)
    cls.__FIREFLY__.set_command(command)


def set_query(cls, query: ff.TypeOfQuery):
    check_for_meta(cls)
    cls.__FIREFLY__.set_query(query)


def get_endpoints(cls):
    check_for_meta(cls)
    return cls.__FIREFLY__.get_endpoints()


def get_events(cls):
    check_for_meta(cls)
    return cls.__FIREFLY__.get_events()


def get_command(cls):
    check_for_meta(cls)
    return cls.__FIREFLY__.get_command()


def get_query(cls):
    check_for_meta(cls)
    return cls.__FIREFLY__.get_query()


def has_endpoints(cls):
    check_for_meta(cls)
    return cls.__FIREFLY__.has_endpoints()


def is_event_listener(cls):
    check_for_meta(cls)
    return cls.__FIREFLY__.is_event_listener()


def is_command_handler(cls):
    check_for_meta(cls)
    return cls.__FIREFLY__.is_command_handler()


def is_query_handler(cls):
    check_for_meta(cls)
    return cls.__FIREFLY__.is_query_handler()


def merge(a, b, path=None):
    if path is None:
        path = []
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                merge(a[key], b[key], path + [str(key)])
            elif a[key] == b[key]:
                pass
            else:
                a[key] = b[key]
                # raise Exception('Conflict at %s' % '.'.join(path + [str(key)]))
        else:
            a[key] = b[key]
    return a
