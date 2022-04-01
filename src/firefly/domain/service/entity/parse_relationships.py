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

from dataclasses import fields
from pprint import pprint
from typing import Type, List, get_type_hints

import inflection

import firefly.domain as ffd
from ...utils import is_type_hint, get_args, get_origin
from ...service.core.domain_service import DomainService


class ParseRelationships(DomainService):
    _stack: list = None

    def __call__(self, entity: Type[ffd.Entity]):
        self._stack = []
        return self._get_relationships(entity)

    def _get_relationships(self, entity: Type[ffd.Entity]):
        entry = list(filter(lambda s: s[0] is entity, self._stack))
        if len(entry) > 0:
            return entry[0][1]

        relationships = {}
        self._stack.append((entity, relationships))
        annotations_ = get_type_hints(entity)
        for field in fields(entity):
            k = field.name
            v = annotations_[k]

            if k.startswith('_'):
                continue

            if isinstance(v, type) and issubclass(v, ffd.Entity):
                print(f"        {k}")
                relationships[k] = {
                    'field_name': k,
                    'target': v,
                    'this_side': 'one',
                    'relationships': self._get_relationships(v),
                    'fqtn': inflection.tableize(v.get_fqn()),
                    'metadata': field.metadata,
                    'other_side': None,
                    'target_property': None,
                }

                for child_k, child_v in relationships[k]['relationships'].items():
                    target = child_v['target']
                    if target is entity:
                        relationships[k]['other_side'] = child_v['this_side']
                        relationships[k]['target_property'] = child_k
                    elif is_type_hint(target) and target is List and get_args(target)[0] is entity:
                        relationships[k]['other_side'] = child_v['this_side']
                        relationships[k]['target_property'] = child_k

            elif is_type_hint(v):
                origin = get_origin(v)
                args = get_args(v)
                if origin is List and issubclass(args[0], ffd.Entity):
                    relationships[k] = {
                        'field_name': k,
                        'target': args[0],
                        'this_side': 'many',
                        'relationships': self._get_relationships(args[0]),
                        'fqtn': inflection.tableize(args[0].get_fqn()),
                        'metadata': field.metadata,
                        'other_side': None,
                        'target_property': None,
                    }

                    for child_k, child_v in relationships[k]['relationships'].items():
                        target = child_v['target']
                        if child_v['metadata'].get('type') is list and target is entity:
                            relationships[k]['other_side'] = child_v['this_side']
                            relationships[k]['target_property'] = child_k
                        elif target is entity:
                            relationships[k]['other_side'] = child_v['this_side']
                            relationships[k]['target_property'] = child_k

        self._stack.pop()

        return relationships
