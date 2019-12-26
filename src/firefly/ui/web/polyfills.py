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
from datetime import datetime, date

# __pragma__('kwargs')
# __pragma__('opov')

document = {}
window = {}


class Console:
    def log(self, *args):
        pass

    def error(self, *args):
        pass


console = Console()  # __:skip


class ABC:
    pass


def abstractmethod(cls):
    return cls


class ABCMeta:
    pass


class MessageMeta:
    pass


MISSING = 'missing'


def dataclass(_cls=None, *, init=True, repr=True, eq=True, order=False,
              unsafe_hash=False, frozen=False):
    return _cls
    if _cls is None:
        def wrapper(_cls):
            return _do_make_dataclass(_cls, init=init, repr=repr, eq=eq, order=order, unsafe_hash=unsafe_hash,
                                      frozen=frozen)

        return wrapper

    return _do_make_dataclass(_cls, init=init, repr=repr, eq=eq, order=order, unsafe_hash=unsafe_hash,
                              frozen=frozen)


def _do_make_dataclass(_cls, *, init=True, repr=True, eq=True, order=False,
              unsafe_hash=False, frozen=False):
    if init:
        def __init(self, **kwargs):
            for k, v in kwargs.items():
                if hasattr(self, k):
                    setattr(self, k, v)

        _cls['__init__'] = __init

    return _cls


def fields(*args, **kwargs):
    console.log('fields() called')


def field(*, default=MISSING, default_factory=MISSING, init=True, repr=True,
          hash=None, compare=True, metadata=None):
    if callable(default_factory):
        return default_factory()
    return default


def asdict():
    pass


def is_dataclass():
    pass


def make_dataclass(cls_name, fields, *, bases=(), namespace=None, init=True,
                   repr=True, eq=True, order=False, unsafe_hash=False,
                   frozen=False):
    return type.__new__(type, cls_name, bases, fields)


class Entity:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, v)

    def to_dict(self):
        ret = {}
        for k in dir(self):
            if not k.startswith('__'):
                ret[k] = getattr(self, k)

        return ret


class AggregateRoot(Entity):
    pass


class Empty:
    pass


def id_(is_uuid: bool = True):
    return 'TODO: Generate uuid in JS' if is_uuid else None


def list_():
    return []


def dict_():
    return {}


def now():
    return datetime.now()


def today():
    return date.today()


def required():
    return Empty()


def optional(default=MISSING):
    return default


def hidden():
    return None


# Mithril

class Route:
    prefix = None

    def __call__(self, root, default_route, routes):
        pass

    def set(self, path):
        pass

    def get(self):
        pass


class M:
    def __init__(self):
        self.route = Route()

    def __call__(self, selector, attrs, children=None):
        pass

    def render(self):
        pass

    def mount(self, element, component):
        pass

    def request(self, options):
        pass

    def jsonp(self, options):
        pass

    def parseQueryString(self, querystring):
        pass

    def buildQueryString(self, obj):
        pass

    def trust(self, html):
        pass

    def redraw(self):
        pass


m = M()


class Stream:
    def __init__(self, *args, **kwargs):
        pass

    def __call__(self, *args, **kwargs):
        pass


def uuid1():
    return 'TODO: Implement JS uuid'


uuid = {
    'uuid1': uuid1
}


class TypeVar:
    def __init__(self, *args, **kwargs):
        pass


Union = {}
Type = {}
Tuple = {}
List = {}


def get_type_hints():
    pass


inflection = {}
