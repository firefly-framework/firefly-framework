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
from typing import List, Type

import firefly.domain as ffd


class LoadInfrastructureLayer(ffd.ApplicationService):
    _context_map: ffd.ContextMap = None
    _agent_factory: ffd.AgentFactory = None
    _deferred: list = []

    def __call__(self, **kwargs):
        for context in self._context_map.contexts:
            self._deferred = []
            for cls in self._load_module(context):
                self._register_object(cls, context)
            for cls in self._deferred:
                self._register_object(cls, context)

        self.dispatch(ffd.InfrastructureLayerLoaded())

    def _register_object(self, cls: Type[ffd.MetaAware], context: ffd.Context):
        if cls.is_agent():
            self._agent_factory.register(cls.get_agent(), context.container.build(cls))

        elif issubclass(cls, ffd.AgentExtension) and cls.is_agent_extension():
            for_, step = cls.get_agent_extension()
            try:
                getattr(self._agent_factory(for_), step)(context.container.build(cls))
            except ffd.ConfigurationError:
                self._deferred.append(cls)

    @staticmethod
    def _load_module(context: ffd.Context) -> List[Type[ffd.MetaAware]]:
        module_name = context.config.get('infrastructure_module', '{}.infrastructure')
        try:
            module = importlib.import_module(module_name.format(context.name))
        except (ModuleNotFoundError, KeyError):
            return []

        ret = []
        for k, v in module.__dict__.items():
            if not inspect.isclass(v):
                continue
            if issubclass(v, ffd.MetaAware):
                ret.append(v)

        return ret
