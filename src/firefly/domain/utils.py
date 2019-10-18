from __future__ import annotations

import enum
import importlib
import inspect
import sys
from abc import ABCMeta, ABC
from dataclasses import is_dataclass, fields, dataclass
from time import sleep

import typing
import firefly.domain as ffd


def retry(cb, valid_cb=None, wait: int = 1, backoff: bool = True, retries: int = 10, catch=Exception):
    while retries > 0:
        try:
            ret = cb()
            if valid_cb is not None and not valid_cb(ret):
                raise RuntimeError('valid_cb is false-y for return value')
            return ret
        except catch as e:
            retries -= 1
            if retries <= 0:
                raise e
            sleep(wait)
            if backoff:
                wait *= 2


def get_arguments(c: callable) -> dict:
    ret = {}
    sig = dict(inspect.signature(c).parameters)

    for k, v in typing.get_type_hints(c).items():
        if k == 'return':
            continue

        ret[k] = {
            'type': v,
            'default': sig[k].default,
            'kind': sig[k].kind,
        }

    return ret


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


def build_argument_list(params: dict, obj: typing.Union[typing.Callable, type]):
    args = {}
    field_dict = {}
    is_dc = False

    if is_dataclass(obj):
        is_dc = True
        field_dict = {}
        # noinspection PyDataclass
        for field_ in fields(obj):
            field_dict[field_.name] = field_
        sig = inspect.signature(obj.__init__)
        types = typing.get_type_hints(obj)
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
        elif param.default is not None:
            required = True

        type_ = types[name] if name in types else None
        if isinstance(type_, type) and issubclass(type_, ffd.Entity):
            entity_args = build_argument_list(params, type_)
            args[name] = type_(**entity_args)
            for key in entity_args.keys():
                if key != type_.id_name():
                    del params[key]
                    if key in args:
                        del args[key]
        elif name in params:
            args[name] = params[name]
        elif name.endswith('_') and name.rstrip('_') in params:
            args[name] = params[name.rstrip('_')]
        elif required is True:
            raise ffd.MissingArgument(f'Argument: {name} is required')

    return args


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


class EntityMeta(ABCMeta):
    def __new__(mcs, name, bases, dct, **kwargs):
        ret = super().__new__(mcs, name, bases, dct)
        ret = dataclass(ret, eq=False)

        is_aggregate = False
        for c in bases:
            # We can't import AggregateRoot for a proper issubclass check without getting a circular reference.
            if 'AggregateRoot' in str(c):
                is_aggregate = True
                break

        if is_aggregate:
            if 'create_on' in kwargs:
                ret = ffd.on(kwargs['create_on'], action='create')(ret)
            if 'delete_on' in kwargs:
                ret = ffd.on(kwargs['delete_on'], action='delete')(ret)
            if 'update_on' in kwargs:
                ret = ffd.on(kwargs['update_on'], action='update')(ret)

        return ret

    def __init__(cls, name, bases, dct, **kwargs):
        super().__init__(name, bases, dct)
        cls._c = None

    # noinspection PyDataclass
    @property
    def c(cls):
        if cls._c is None:
            from .repository.search_criteria import AttrFactory
            cls._c = AttrFactory([x.name for x in fields(cls)])
        return cls._c


class ValueMeta(type):
    def __new__(mcs, name, bases, dct, **kwargs):
        ret = type.__new__(mcs, name, bases, dct)
        return dataclass(ret, frozen=True)


class MessageMeta(ABCMeta):
    def __new__(mcs, name, bases, dct, **kwargs):
        if 'fields_' in kwargs and 'annotations_' in kwargs:
            for k, v in kwargs['fields_'].items():
                dct[k] = ffd.optional(default=v)
            if '__annotations__' in dct:
                dct['__annotations__'].update(kwargs['annotations_'])
            else:
                dct['__annotations__'] = kwargs['annotations_']

        ret = super().__new__(mcs, name, bases, dct)

        return dataclass(ret, eq=False, repr=False)


class ContextAware(ABC):
    @classmethod
    def get_class_context(cls):
        parts = cls.__module__.split('.')
        # KLUDGE For integration / acceptance testing
        return parts[0] if parts[0] != 'test_src' else parts[1]

    @classmethod
    def get_fqn(cls):
        return f'{cls.get_class_context()}.{cls.__name__}'


class FireflyType(ContextAware, ABC):
    _context: str = None

    def __str__(self):
        return f'{self._context}.{self.__class__.__name__}' \
            if self._context is not None else self.__class__.__name__

    def __repr__(self):
        return str(self)

    def is_this(self, this: typing.Any):
        if isinstance(this, str) and this == str(self):
            return True
        try:
            return isinstance(self, this) and self.__class__.__name__ == this.__name__
        except TypeError:
            return False

    def get_context(self):
        return self._context
