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
import typing
from abc import ABC
from typing import Tuple
from unittest.mock import MagicMock


class Container(ABC):
    def __init__(self):
        self._cache = {}
        self._annotations = None
        self._unannotated = None
        self._child_containers = []

    def __getattribute__(self, item: str):
        if item.startswith('_'):
            return object.__getattribute__(self, item)

        if item in self._cache:
            return self._cache[item]()

        obj = object.__getattribute__(self, item)

        if inspect.ismethod(obj) and obj.__name__ != '<lambda>':
            return obj

        if not callable(obj):
            raise AttributeError(f'Attribute {item} is not callable.')

        if inspect.isclass(obj):
            obj = self.build(obj)
            self._cache[item] = lambda: obj
        elif inspect.isfunction(obj) or inspect.ismethod(obj):
            obj = obj()
            if inspect.isfunction(obj):
                self._cache[item] = obj
            else:
                self._cache[item] = lambda: obj
        else:
            self._cache[item] = lambda: obj

        return self._cache[item]()

    def _search_child_containers(self, item: str):
        for container in self._child_containers:
            if item in dir(container):
                return getattr(container, item)

        raise AttributeError(item)

    def build(self, class_: object, **kwargs):
        a = self.autowire(class_, kwargs)
        try:
            return a()
        except TypeError as e:
            if 'instantiate abstract class' not in str(e):
                raise e

    def mock(self, class_, **kwargs):
        a = self.autowire(class_, kwargs, with_mocks=True)
        try:
            return a()
        except TypeError as e:
            if 'instantiate abstract class' not in str(e):
                raise e

    def autowire(self, class_, params: dict = None, with_mocks: bool = False):
        if hasattr(class_, '__original_init'):
            return class_

        if inspect.isclass(class_) and hasattr(class_, '__init__'):
            class_ = self._wrap_constructor(class_, params, with_mocks)

        ret = self._inject_properties(class_, with_mocks)

        return ret

    def register_container(self, container):
        if container not in self._child_containers:
            self._child_containers.append(container)
        self._unannotated = None
        for c in self._child_containers:
            c._unannotated = None
        return self

    def match(self, name: str, type_):
        t = self._find_by_type(self._get_annotations(), type_)

        if len(t) == 1:
            t = str(t[0])
        elif len(t) == 0:
            t = None
        else:
            x = None
            for item in t:
                if name == item or name.lstrip('_') == item:
                    if getattr(self, item) is None:
                        continue
                    x = item
                    break
            t = x

        # Found type in the container
        if t is not None:
            return getattr(self, t)

        # Found object with same name in container
        elif t is None and name in self._get_unannotated():
            return getattr(self, name)

    def get_registered_services(self):
        ret = {}
        annotations = typing.get_type_hints(type(self))
        for k, v in self.__class__.__dict__.items():
            if not str(k).startswith('_'):
                ret[k] = annotations[k] if k in annotations else ''

        return ret

    def clear_annotation_cache(self):
        self._annotations = None

    def _wrap_constructor(self, class_, params, with_mocks):
        init = class_.__init__

        def init_wrapper(*args, **kwargs):
            constructor_args = self._get_constructor_args(class_)

            for name, type_ in constructor_args.items():
                if type_ == Container:
                    kwargs[name] = self
                    continue

                if type_ is not str and with_mocks is True:
                    kwargs[name] = MagicMock(spec=type_ if type_ != 'nil' else None)
                    continue

                # Search this container, and any child containers for a match
                t = self.match(name, type_)
                if t is not None and name not in kwargs:
                    kwargs[name] = t

                # This is a string parameter. Look for params/environment variables to inject.
                elif type_ is str:
                    t = self._find_parameter(name)
                    if t is not None:
                        kwargs[name] = t

            if params is not None:
                for key, value in params.items():
                    kwargs[key] = value

            return init(*args, **kwargs)

        setattr(class_, '__original_init', init)
        class_.__init__ = init_wrapper

        return class_

    def _inject_properties(self, class_, with_mocks: bool):
        properties, annotations = self._get_class_tree_properties(class_)
        unannotated = self._get_unannotated()

        for k, v in properties.items():
            if str(k).startswith('__') or v is not None:
                continue

            try:
                if k in annotations and isinstance(self, annotations[k]):
                    setattr(class_, k, self)
                    continue
            except TypeError:
                pass

            if with_mocks:
                setattr(class_, k, MagicMock(spec=annotations[k] if k in annotations else None))
            elif k in annotations:
                if annotations[k] is str:
                    t = self._find_parameter(k)
                    if t is None:
                        t = self._find_parameter(k.lstrip('_'))
                    if t is not None:
                        setattr(class_, k, t)
                        continue
                t = self.match(k, annotations[k])
                if t is not None:
                    setattr(class_, k, t)
            elif k in unannotated:
                setattr(class_, k, getattr(self, k))
            elif k.lstrip('_') in unannotated:
                setattr(class_, k, getattr(self, k.lstrip('_')))

        return class_

    def _get_class_tree_properties(self, class_: typing.Any, properties: dict = None, annotations: dict = None)\
            -> Tuple[dict, dict]:
        if properties is None and annotations is None:
            properties = {}
            annotations = {}

        properties.update(class_.__dict__)
        try:
            annotations.update(typing.get_type_hints(class_))
        except AttributeError:
            pass

        if hasattr(class_, '__bases__'):
            for base in class_.__bases__:
                properties, annotations = self._get_class_tree_properties(base, properties, annotations)

        return properties, annotations

    def _get_annotations(self):
        return typing.get_type_hints(type(self))

    def _get_unannotated(self):
        annotations_ = self._get_annotations()
        if self._unannotated is None:
            # unannotated = inspect.getmembers(type(self), lambda a: not (inspect.isroutine(a)))
            unannotated = inspect.getmembers(type(self))
            self._unannotated = []
            for entry in unannotated:
                if entry[0] not in annotations_:
                    self._unannotated.append(entry[0])
            for child_container in self._child_containers:
                self._unannotated.extend(child_container._get_unannotated())

        return self._unannotated

    @staticmethod
    def _get_constructor_args(class_):
        init = class_.__init__
        if hasattr(class_, '__original_init'):
            init = getattr(class_, '__original_init')
        try:
            constructor_args = typing.get_type_hints(init)
        except NameError:
            return {}
        items = {}
        items.update(constructor_args)
        for arg in constructor_args.keys():
            if arg != 'self' and arg not in items:
                items[arg] = 'nil'

        return items

    @staticmethod
    def _find_by_type(available: dict, t):
        ret = []

        for key, value in available.items():
            try:
                if issubclass(value, t):
                    ret.append(key)
            except TypeError:
                try:
                    if str(value) == str(t):
                        ret.append(key)
                except RecursionError:
                    pass

        return ret

    @staticmethod
    def _find_parameter(name: str):
        if name in os.environ:
            return os.environ.get(name)
        elif name.upper() in os.environ:
            return os.environ.get(name.upper())


class MockContainer(Container):
    pass


mock_container = MockContainer()


def inject_mocks(class_, **kwargs):
    return mock_container.mock(class_, **kwargs)
