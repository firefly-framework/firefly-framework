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

from dataclasses import is_dataclass
from datetime import datetime, date
from typing import Union, List, Type

import firefly.domain as ffd
import regex


class EntityAttributeSpy:
    def __init__(self, type_: Type[ffd.ValueObject] = None):
        self._type = type_

    def __getattribute__(self, item):
        if object.__getattribute__(self, '_type') is not None:
            t = object.__getattribute__(self, '_type')
            valid = False
            if is_dataclass(t) and item in t.__dataclass_fields__:
                valid = True
            elif hasattr(t, item):
                valid = True
            if not valid:
                raise AttributeError(f"'{t.__name__}' object has no attribute '{item}'")
        return Attr(item)


class AttributeString(str):
    pass


class Invalid:
    pass


INVALID = Invalid()


class Attr:
    def __init__(self, attr: str, default=None):
        self.attr = AttributeString(attr)
        self.default = default

    def __getattribute__(self, item):
        try:
            return object.__getattribute__(self, item)
        except AttributeError:
            raise ffd.InvalidOperand(f"Use of '{item}' is not currently supported.")

    def is_none(self):
        return BinaryOp(self.attr, 'is', 'null')

    def is_false(self):
        return BinaryOp(self.attr, 'is', False)

    def is_true(self):
        return BinaryOp(self.attr, 'is', True)

    def is_in(self, set_):
        return BinaryOp(self.attr, 'in', set_)

    def contains(self, value):
        return BinaryOp(self.attr, 'contains', value)

    def startswith(self, value):
        return BinaryOp(self.attr, 'startswith', value)

    def lower(self):
        self.attr = AttributeString(f'LOWER({self.attr})')
        return self

    def upper(self):
        self.attr = AttributeString(f'UPPER({self.attr})')
        return self

    def endswith(self, value):
        return BinaryOp(self.attr, 'endswith', value)

    def __eq__(self, other):
        return BinaryOp(self.attr, '==', other)

    def __ne__(self, other):
        return BinaryOp(self.attr, '!=', other)

    def __gt__(self, other):
        return BinaryOp(self.attr, '>', other)

    def __ge__(self, other):
        return BinaryOp(self.attr, '>=', other)

    def __lt__(self, other):
        return BinaryOp(self.attr, '<', other)

    def __le__(self, other):
        return BinaryOp(self.attr, '<=', other)

    def __repr__(self):
        return self.attr


class AttrFactory:
    def __init__(self, fields: List[str]):
        self._fields = fields

    def __getattr__(self, item):
        if item in self._fields:
            return Attr(item)
        return object.__getattribute__(self, item)


class BinaryOp:
    def __init__(self, lhv, op, rhv):
        self.lhv = lhv
        self.op = op
        self.rhv = rhv

    def to_dict(self):
        return self._do_to_dict(self)

    def _do_to_dict(self, bop: BinaryOp):
        ret = {'l': None, 'o': bop.op, 'r': None}

        if isinstance(bop.lhv, BinaryOp):
            ret['l'] = self._do_to_dict(bop.lhv)
        elif isinstance(bop.lhv, (Attr, AttributeString)):
            ret['l'] = f'a:{str(bop.lhv)}'
        else:
            ret['l'] = bop.lhv

        if isinstance(bop.rhv, BinaryOp):
            ret['r'] = self._do_to_dict(bop.rhv)
        elif isinstance(bop.rhv, (Attr, AttributeString)):
            ret['r'] = f'a:{str(bop.rhv)}'
        else:
            ret['r'] = bop.rhv

        return ret

    @classmethod
    def from_dict(cls, data: dict):
        if isinstance(data['l'], dict):
            lhv = cls.from_dict(data['l'])
        elif isinstance(data['l'], str) and data['l'].startswith('a:'):
            lhv = Attr(data['l'].split(':')[1])
        else:
            lhv = data['l']

        if isinstance(data['r'], dict):
            rhv = cls.from_dict(data['r'])
        elif isinstance(data['r'], str) and data['r'].startswith('a:'):
            rhv = Attr(data['r'].split(':')[1])
        else:
            rhv = data['r']

        return BinaryOp(lhv, data['o'], rhv)

    def matches(self, data: Union[ffd.Entity, dict]) -> bool:
        if isinstance(data, ffd.Entity):
            data = data.to_dict(force_all=True)

        return self._do_match(self, data)

    def _do_match(self, bop: BinaryOp, data: dict) -> bool:
        if isinstance(bop.lhv, BinaryOp):
            lhv = self._do_match(bop.lhv, data)
        elif isinstance(bop.lhv, AttributeString):
            if '(' in bop.lhv:
                lhv = self._parse_attribute_string(bop.lhv, data)
            else:
                lhv = data[bop.lhv]
        elif isinstance(bop.lhv, Attr):
            if '(' in bop.lhv.attr:
                lhv = self._parse_attribute_string(bop.lhv.attr, data)
            else:
                lhv = data[bop.lhv.attr]
        else:
            lhv = bop.lhv

        if isinstance(bop.rhv, BinaryOp):
            rhv = self._do_match(bop.rhv, data)
        elif isinstance(bop.rhv, AttributeString):
            if '(' in bop.rhv:
                rhv = self._parse_attribute_string(bop.rhv, data)
            else:
                rhv = data[bop.rhv]
        elif isinstance(bop.rhv, Attr):
            if '(' in bop.rhv.attr:
                rhv = self._parse_attribute_string(bop.rhv.attr, data)
            else:
                rhv = data[bop.rhv.attr]
        else:
            rhv = bop.rhv

        if bop.op == '==':
            return lhv == rhv
        if bop.op == '!=':
            return lhv != rhv
        if bop.op == '>':
            return lhv > rhv
        if bop.op == '<':
            return lhv < rhv
        if bop.op == '>=':
            return lhv >= rhv
        if bop.op == '<=':
            return lhv <= rhv
        if bop.op == 'is':
            return lhv is rhv if rhv != 'null' else lhv is None
        if bop.op == 'in':
            return lhv in rhv
        if bop.op == 'contains':
            return rhv in lhv
        if bop.op == 'startswith':
            return str(lhv).startswith(rhv)
        if bop.op == 'endswith':
            return str(lhv).endswith(rhv)
        if bop.op == 'and':
            return lhv and rhv
        if bop.op == 'or':
            return lhv or rhv

        raise ffd.LogicError(f"Don't know how to handle op: {bop.op}")

    @staticmethod
    def _parse_attribute_string(attr: str, data: dict):
        matches = list(map(lambda rr: rr[2], regex.findall(r'((\w)\((?R)\))|(\w+)', attr)))
        attribute = matches.pop()
        value = data[attribute]

        for func in reversed(matches):
            if func == 'LOWER':
                value = value.lower()
            elif func == 'UPPER':
                value = value.upper()

        return value

    def __and__(self, other):
        return BinaryOp(self, 'and', other)

    def __or__(self, other):
        return BinaryOp(self, 'or', other)

    def prune(self, fields: list):
        data = self._prune(fields, self.to_dict())
        if data is INVALID:
            data = {'l': 1, 'o': '==', 'r': 1}
        return BinaryOp.from_dict(data)

    def _prune(self, fields: list, data: dict):
        if isinstance(data['l'], dict):
            result = self._prune(fields, data['l'])
            if result is INVALID:
                if data['o'] == 'and':
                    data['l'] = {'l': 1, 'o': '==', 'r': 1}
                else:
                    data['l'] = {'l': 1, 'o': '!=', 'r': 1}
        elif isinstance(data['l'], str) and len(data['l']) > 2 and \
                data['l'].startswith('a:') and data['l'][2:] not in fields:
            return INVALID

        if isinstance(data['r'], dict):
            result = self._prune(fields, data['r'])
            if result is INVALID:
                if data['o'] == 'and':
                    data['r'] = {'l': 1, 'o': '==', 'r': 1}
                else:
                    data['r'] = {'l': 1, 'o': '!=', 'r': 1}
        elif isinstance(data['r'], str) and len(data['r']) > 2 and \
                data['r'].startswith('a:') and data['r'][2:] not in fields:
            return INVALID

        if isinstance(data['r'], dict) and isinstance(data['l'], dict):
            if data['l']['l'] == 1 and data['l']['r'] == 1 and data['r']['l'] == 1 and data['r']['r'] == 1:
                return INVALID

        return data

    def to_sql(self):
        sql, params, counter = self._to_sql()
        return sql, params

    def _to_sql(self, counter: int = None, params: dict = None):
        counter = counter or 1
        params = params or {}
        lhv, params, counter = self._process_op(self.lhv, params, counter)
        if self.op == 'is' and (self.rhv == 'null' or self.rhv is None):
            rhv = 'null'
        else:
            rhv, params, counter = self._process_op(self.rhv, params, counter)

        ret_op = self.op
        if ret_op == 'startswith':
            ret_op = 'like'
            rhv = f"CONCAT({rhv}, '%')"
        elif ret_op == 'endswith':
            ret_op = 'like'
            rhv = f"CONCAT('%', {rhv})"

        return f'({lhv} {ret_op.replace("==", "=")} {rhv})', params, counter

    @staticmethod
    def _process_op(v, params: dict, counter: int):
        if isinstance(v, BinaryOp):
            v, p, counter = v._to_sql(counter, params)
            params.update(p)
        elif isinstance(v, (list, tuple)):
            placeholders = []
            for i in v:
                var = f'var{counter}'
                counter += 1
                placeholders.append(f':{var}')
                params[var] = i
            v = f'({",".join(placeholders)})'
        elif not isinstance(v, (Attr, AttributeString)):
            var = f'var{counter}'
            counter += 1
            params[var] = v
            v = f':{var}'

        return v, params, counter

    def __repr__(self):
        return f'({self.lhv} {self.op} {self.rhv})'

    def __eq__(self, other):
        return isinstance(other, BinaryOp) and self.to_dict() == other.to_dict()
