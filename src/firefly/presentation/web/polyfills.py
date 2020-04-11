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
# __pragma__('js', '{}', "const uuidv1 = require('uuid/v1');")


document = {}
window = {}
process = {}
JSON = {}
moment = {}
navigator = {}
this = {}  # __:skip


# __pragma__('skip')
def uuidv1():
    pass


def require(*args, **kwargs):
    pass
# __pragma__('noskip')


class Uuid:
    def __init__(self):
        self.uuid1 = uuidv1


uuid = Uuid()


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


class MissingType:
    pass


MISSING = MissingType()


def field(*, default=MISSING, default_factory=MISSING, init=True, repr=True,
          hash=None, compare=True, metadata=None):
    return {
        'default': default,
        'default_factory': default_factory,
        'init': init,
        'repr': repr,
        'hash': hash,
        'compare': compare,
        'metadata': metadata,
    }


class Field:
    pass


def asdict():
    pass


def is_dataclass():
    pass


def make_dataclass(cls_name, fields, *, bases=(), namespace=None, init=True,
                   repr=True, eq=True, order=False, unsafe_hash=False,
                   frozen=False):
    return type.__new__(type, cls_name, bases, fields)


class DataClassBase:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            if hasattr(self, k) and not callable(getattr(self, k)):
                # TODO Figure out why setattr doesn't work with "name." Could be a bug in transcrypt.
                if k == 'name':
                    self.name = v
                else:
                    setattr(self, k, v)

    def to_dict(self):
        ret = {}
        for k in dir(self):
            if not k.startswith('__') and not callable(getattr(self, k)):
                ret[k] = getattr(self, k)

        return ret


class Entity(DataClassBase):
    def __init__(self, **kwargs):
        for k in dir(self):
            if k.startswith('__') or not isinstance(getattr(self, k), str):
                continue
            if getattr(self, k) == '__gen_uuid__':
                kwargs[k] = uuidv1()
        super().__init__(**kwargs)


class AggregateRoot(Entity):
    pass


class ValueObject(DataClassBase):
    pass


class Message(DataClassBase):
    headers: dict = {}
    _id: str = None
    _context: str = None
    _name: str = None
    _type: str = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._id = uuidv1()

    def get_context(self):
        return self._context

    def to_dict(self):
        ret = super().to_dict()
        if isinstance(self, Command):
            ret['_type'] = 'command'
        elif isinstance(self, Event):
            ret['_type'] = 'event'
        else:
            ret['_type'] = 'query'

        ret['_name'] = self.__class__.__name__

        return ret


class Command(Message):
    pass


class Query(Message):
    pass


class Event(Message):
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
Any = {}


def get_type_hints():
    pass


inflection = {}
