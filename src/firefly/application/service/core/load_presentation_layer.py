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
from typing import List

import firefly.domain as ffd


class LoadPresentationLayer(ffd.ApplicationService):
    _context_map: ffd.ContextMap = None

    def __call__(self, **kwargs):
        for context in self._context_map.contexts:
            for obj in self._load_module(context):
                context.ports.append(obj)

        self.dispatch(ffd.PresentationLayerLoaded())

    @staticmethod
    def _load_module(context: ffd.Context) -> List[object]:
        module_name = context.config.get('ui_module', '{}.ui')
        try:
            module = importlib.import_module(module_name.format(context.name))
        except (ModuleNotFoundError, KeyError):
            return []

        ret = []
        for k, v in module.__dict__.items():
            if not inspect.isclass(v):
                continue
            if hasattr(v, '__ff_port'):
                ret.append(v)

        return ret
