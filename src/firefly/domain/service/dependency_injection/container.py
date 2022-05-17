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
from pprint import pprint
from typing import Tuple
from unittest.mock import MagicMock

import inflection
from devtools import debug

import firefly.domain as ffd
from pydantic.dataclasses import dataclass

DO_NOT_RESET = ('routes_rest_router',)


class ContainerProperty:
    def __init__(self, constructor, container):
        self._constructor = constructor
        self._container = container

    def __call__(self, _):
        return self._constructor(self._container)


@dataclass
class Constructor:
    type: type
    name: str = None
    constructor: typing.Any = None
    instance: object = None

    def __call__(self, container):
        if self.instance is None:
            try:
                self.instance = self.constructor(container)
            except TypeError as e:
                if 'abstract class' not in str(e):
                    raise TypeError(self.name) from e
        return self.instance

    def matches(self, type_: type = None, name: str = None):
        if type_ is type:
            return False

        if inspect.isabstract(type_) and inspect.isclass(self.type) and issubclass(self.type, type_):
            return True

        if type_ is not None:
            if self.type is type_:
                return True

        return name is not None and (name == self.name or name.lstrip('_') == self.name)


class Container(ABC):
    _static_dependencies = []

    def __init__(self):
        self._stack = []
        self._constructors = []

        for dep in self.__class__._static_dependencies:
            self.register_object(**dep)

    def __getattribute__(self, item: str):
        if item.startswith('_'):
            return object.__getattribute__(self, item)

        constructor = self._find_constructor(name=item)
        if constructor is not None:
            return constructor(self)

        return object.__getattribute__(self, item)

    def reset(self):
        self._stack = []
        for constructor in self._constructors:
            if constructor.name.startswith('sqlalchemy_') or constructor.name in DO_NOT_RESET:
                continue
            constructor.instance = None

    @classmethod
    def use(cls, name: str, type_: typing.Type = type, constructor: typing.Optional[typing.Callable] = None):
        cls._static_dependencies.append({
            'name': name,
            'type_': type_,
            'constructor': constructor,
        })

    def register_object(self, name: str, type_: typing.Type = type,
                        constructor: typing.Optional[typing.Callable] = None, force: bool = False):
        if name.endswith('aware'):
            return

        c = self._find_constructor(type_, name)
        if c is not None and force is False:
            return

        if constructor is None:
            def constructor(s):
                self.autowire(type_)
                return type_()

        if c is None:
            self._constructors.append(Constructor(
                name=name,
                type=type_,
                constructor=constructor
            ))
        else:
            c.constructor = constructor

    def debug(self):
        for constructor in self._constructors:
            print(constructor)

    def build(self, class_: type, **kwargs):
        name = inflection.underscore(class_.__name__)
        self.register_object(name, class_)
        return getattr(self, name)

    def mock(self, class_, **kwargs):
        a = self.autowire(class_, kwargs, with_mocks=True)
        try:
            return a()
        except TypeError as e:
            if 'instantiate abstract class' not in str(e):
                raise e

    def autowire(self, class_, with_mocks: bool = False):
        if class_ in self._stack:
            return class_
        self._stack.append(class_)

        properties, annotations_ = self._get_class_tree_properties(class_)
        for k, v in properties.items():
            if str(k).startswith('__'):
                continue

            try:
                if k in annotations_ and isinstance(self, annotations_[k]):
                    setattr(class_, k, self)
                    continue
            except TypeError:
                pass

            if with_mocks:
                setattr(class_, k, property(
                    fget=lambda key=k: MagicMock(spec=annotations_[k] if k in annotations_ else None))
                )
            else:
                if annotations_.get(k) is str:
                    t = self._find_parameter(k)
                    if t is None:
                        t = self._find_parameter(k.lstrip('_'))
                    if t is not None:
                        setattr(class_, k, t)
                        continue
                else:
                    constructor = self._find_constructor(annotations_.get(k), k)
                    if constructor is not None:
                        if constructor.instance is None:
                            constructor.instance = constructor.constructor(self)
                        setattr(class_, k, property(fget=ContainerProperty(constructor, self)))

        # self._stack.pop()
        return class_

    def _find_constructor(self, type_: type = None, name: str = None):
        for constructor in self._constructors:
            if constructor.matches(type_, name):
                return constructor

    def _get_class_tree_properties(self, class_: typing.Any, properties: dict = None, annotations_: dict = None)\
            -> Tuple[dict, dict]:
        if properties is None and annotations_ is None:
            properties = {}
            annotations_ = {}

        properties.update(class_.__dict__)
        try:
            annotations_.update(typing.get_type_hints(class_))
        except AttributeError:
            if class_.__name__ == 'AuthorizeRequest':
                print("FUCK FACE")
                print(typing.get_type_hints(class_))

        if hasattr(class_, '__bases__'):
            for base in class_.__bases__:
                properties, annotations_ = self._get_class_tree_properties(base, properties, annotations_)

        return properties, annotations_

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
