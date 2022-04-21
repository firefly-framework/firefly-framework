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

from typing import Type, get_type_hints

import firefly.domain as ffd
from firefly.domain.repository.search_criteria import AttributeString, Attr
from firefly.domain.utils import is_type_hint
from sqlalchemy import or_, and_, func
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm import Query, InstrumentedAttribute
from sqlalchemy.sql.elements import BinaryExpression, literal, BindParameter


class Missing:
    pass


missing = Missing()


class ConvertCriteriaToSqlalchemy:
    def __call__(self, entity_type: Type[ffd.Entity], criteria: ffd.SearchCriteria, query: Query):
        filter_ = self._process_node(entity_type, criteria)
        if filter_ is None:
            raise ffd.LogicError(f'Could not construct a valid query given the search criteria: {criteria}')

        return query.filter(filter_)

    def _process_node(self, entity_type: Type[ffd.Entity], criteria: ffd.SearchCriteria):
        code = ''

        a1 = None
        a2 = None
        if isinstance(criteria.lhv, ffd.SearchCriteria):
            a1 = self._process_node(entity_type, criteria.lhv)
        if isinstance(criteria.rhv, ffd.SearchCriteria):
            a2 = self._process_node(entity_type, criteria.rhv)

        if a1 is not None and a2 is not None:
            if criteria.op == 'and':
                return and_(a1, a2)
            else:
                return or_(a1, a2)

        attr = other = missing
        attr_side = None
        if isinstance(criteria.lhv, (AttributeString, Attr)):
            attr_side = 'lhv'
            attr = criteria.lhv
        if isinstance(criteria.rhv, (AttributeString, Attr)):
            if attr is not missing:
                raise RuntimeError()
            attr_side = 'rhv'
            attr = criteria.rhv

        if not isinstance(criteria.lhv, (AttributeString, Attr, ffd.SearchCriteria)):
            other = criteria.lhv

        if not isinstance(criteria.rhv, (AttributeString, Attr, ffd.SearchCriteria)):
            if other is not missing:
                raise RuntimeError()
            other = criteria.rhv

        binary_expression = None
        if attr is not missing and other is not missing:
            if '.' in str(attr):
                parts = str(attr).split('.')
                x = getattr(entity_type, parts.pop(0))
                while len(parts) > 1:
                    x = getattr(x, parts.pop(0))

                key = parts.pop()
                try:
                    binary_expression = x.any(**{key: other})
                except InvalidRequestError:
                    binary_expression = x.has(**{key: other})
            elif code == '':
                left = self._process_modifiers(
                    getattr(entity_type, str(attr)) if attr_side == 'lhv' else literal(other), attr
                )
                right = self._process_modifiers(
                    getattr(entity_type, str(attr)) if attr_side == 'rhv' else literal(other), attr
                )

                if criteria.op in ('=', '<', '<=', '>', '>=', '!='):
                    try:
                        binary_expression = BinaryExpression(left, right, criteria.op)
                    except AttributeError as e:
                        if "self_group" in str(e):
                            raise ffd.LogicError(f"{entity_type.__name__}.{str(attr)} can't be used in comparisons, "
                                                 f"use a property of the entity instead.")
                        raise e
                elif criteria.op == 'is':
                    binary_expression = left.is_(right)
                elif criteria.op == 'is not':
                    binary_expression = left.is_not(right)
                elif criteria.op in ('startswith', 'endswith', 'contains'):
                    fmt = "{}%" if criteria.op == 'startswith' else "%{}" if criteria.op == 'endswith' else "%{}%"
                    left = self._process_modifiers(
                        getattr(entity_type, str(attr)) if attr_side == 'lhv' else literal(fmt.format(other)), attr
                    )
                    right = self._process_modifiers(
                        getattr(entity_type, str(attr)) if attr_side == 'rhv' else literal(fmt.format(other)), attr
                    )
                    binary_expression = left.like(right)

        return binary_expression

    def _process_modifiers(self, value, attr):
        if isinstance(value, InstrumentedAttribute) and attr.has_modifiers():
            for modifier in attr.get_modifiers():
                if modifier == 'UPPER':
                    value = func.upper(value)
                elif modifier == 'LOWER':
                    value = func.lower(value)

        return value
