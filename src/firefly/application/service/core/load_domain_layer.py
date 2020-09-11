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

import firefly.domain as ffd
import inflection


class LoadDomainLayer(ffd.ApplicationService):
    _context_map: ffd.ContextMap = None
    _logger: ffd.Logger = None

    def __call__(self, **kwargs):
        for context in self._context_map.contexts:
            self._load_module(context)
            if 'extends' in context.config:
                base_context = self._context_map.get_context(context.config['extends'])
                self._load_module(
                    context, base_context.config.get('entity_module', '{}.domain').format(base_context.name)
                )
        self.dispatch(ffd.DomainEntitiesLoaded())

    def _load_module(self, context: ffd.Context, module_name: str = None):
        module_name = module_name or context.config.get('entity_module', '{}.domain').format(context.name)
        try:
            module = importlib.import_module(module_name)
        except (ModuleNotFoundError, KeyError):
            return

        for k, v in module.__dict__.items():
            if not inspect.isclass(v):
                continue
            if issubclass(v, ffd.Entity):
                v._logger = self._logger
                context.entities.append(v)
            elif issubclass(v, ffd.ValueObject):
                v._logger = self._logger
            elif issubclass(v, ffd.DomainService) and v is not ffd.DomainService:
                v._logger = self._logger
                v._system_bus = self._system_bus
                name = inflection.underscore(v.__name__)
                setattr(context.container.__class__, name, v)
                if not hasattr(context.container.__class__, '__annotations__'):
                    context.container.__class__.__annotations__ = {}
                context.container.__class__.__annotations__[name] = v
                context.container.clear_annotation_cache()
