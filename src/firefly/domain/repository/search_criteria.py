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
from pprint import pprint
from typing import Union, List, Type

import firefly.domain as ffd
import regex

T = '__FF_SKIP_TYPE'


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


class AttributeString:
    __modifiers = None
    _value: str = None

    def __init__(self, value: str):
        if '(' in value:
            matches = list(map(lambda rr: rr[2], regex.findall(r'((\w)\((?R)\))|(\w+)', str(value))))
            attribute = matches.pop()

            for func in reversed(matches):
                self.add_modifier(func)
            self._value = attribute
        else:
            self._value = str(value)

    def add_modifier(self, modifier: str):
        if self.__modifiers is None:
            self.__modifiers = []
        self.__modifiers.append(modifier)

    def has_modifiers(self):
        return self.__modifiers is not None

    def get_modifiers(self):
        return self.__modifiers

    def __str__(self):
        return str(self._value)

    def __repr__(self):
        ret = ''
        if self.has_modifiers():
            for modifier in self.get_modifiers():
                ret += f'{modifier}('
        ret += str(self)
        if self.has_modifiers():
            for _ in self.get_modifiers():
                ret += ')'

        return ret


class Invalid:
    pass


INVALID = Invalid()


class Attr:
    def __init__(self, attr: str, default=None):
        self.attr = AttributeString(attr)
        self.default = default

    def __getattribute__(self, item):
        if item in ('has_modifiers', 'get_modifiers'):
            return getattr(self.attr, item)

        try:
            return object.__getattribute__(self, item)
        except AttributeError:
            if not item.startswith('_'):
                self.attr = AttributeString(f'{self.attr}.{item}')
                return self
            raise ffd.InvalidOperand(f"Use of '{item}' is not currently supported.")

    def is_none(self):
        return BinaryOp(self.attr, 'is', 'null')

    def is_not_none(self):
        return BinaryOp(self.attr, 'is not', 'null')

    def is_false(self):
        return BinaryOp(self.attr, 'is', False)

    def is_true(self):
        return BinaryOp(self.attr, 'is', True)

    def is_in(self, set_):
        return BinaryOp(self.attr, 'in', set_)

    def not_in(self, set_):
        return BinaryOp(self.attr, 'not in', set_)

    def contains(self, value):
        return BinaryOp(self.attr, 'contains', value)

    def startswith(self, value):
        return BinaryOp(self.attr, 'startswith', value)

    def lower(self):
        self.attr.add_modifier('LOWER')
        return self

    def upper(self):
        self.attr.add_modifier('UPPER')
        return self

    def endswith(self, value):
        return BinaryOp(self.attr, 'endswith', value)

    def reversed(self):
        return self.attr, True

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
        return repr(self.attr)

    def __str__(self):
        return str(self.attr)


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
        return {
            'l': self._get_serialized_value(bop.lhv),
            'o': bop.op,
            'r': self._get_serialized_value(bop.rhv)
        }

    def _get_serialized_value(self, val):
        if isinstance(val, BinaryOp):
            return self._do_to_dict(val)
        elif isinstance(val, (Attr, AttributeString)):
            return f'a:{repr(val)}'
        elif isinstance(val, datetime):
            return f'datetime:{val}'
        elif isinstance(val, date):
            return f'date:{val}'
        else:
            return val

    @classmethod
    def from_dict(cls, data: dict):
        return BinaryOp(
            cls._deserialize_value(data['l']),
            data['o'],
            cls._deserialize_value(data['r'])
        )

    @classmethod
    def _deserialize_value(cls, val):
        if isinstance(val, dict):
            return cls.from_dict(val)
        elif isinstance(val, str) and val.startswith('a:'):
            return Attr(val.split(':')[1])
        elif isinstance(val, str) and val.startswith('datetime:'):
            return ffd.parse(val.split(':')[1])
        elif isinstance(val, str) and val.startswith('date:'):
            return ffd.parse(val.split(':')[1]).date()
        else:
            return val

    def matches(self, data: Union[ffd.Entity, dict]) -> bool:
        if isinstance(data, ffd.Entity):
            data = data.to_dict(force_all=True)

        return self._do_match(self, data)

    def _do_match(self, bop: BinaryOp, data: dict) -> bool:
        if isinstance(bop.lhv, BinaryOp):
            lhv = self._do_match(bop.lhv, data)
        elif isinstance(bop.lhv, AttributeString):
            lhv = self._parse_attribute_string(bop.lhv, data)
        elif isinstance(bop.lhv, Attr):
            lhv = self._parse_attribute_string(bop.lhv.attr, data)
        else:
            lhv = bop.lhv

        if isinstance(bop.rhv, BinaryOp):
            rhv = self._do_match(bop.rhv, data)
        elif isinstance(bop.rhv, AttributeString):
            rhv = self._parse_attribute_string(bop.rhv, data)
        elif isinstance(bop.rhv, Attr):
            rhv = self._parse_attribute_string(bop.rhv.attr, data)
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
        if bop.op == 'is not':
            return lhv is not rhv if rhv != 'null' else lhv is not None
        if bop.op == 'in':
            return lhv in rhv
        if bop.op == 'not in':
            return lhv not in rhv
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
    def _remove_function_calls(attr: str):
        return list(map(lambda rr: rr[2], regex.findall(r'((\w)\((?R)\))|(\w+)', attr))).pop()

    @staticmethod
    def _parse_attribute_string(attr: AttributeString, data: dict):
        value = data[str(attr)]

        if attr.has_modifiers():
            for modifier in attr.get_modifiers():
                if modifier == 'LOWER':
                    value = value.lower()
                elif modifier == 'UPPER':
                    value = value.upper()

        return value

    def __and__(self, other):
        return BinaryOp(self, 'and', other)

    def __or__(self, other):
        return BinaryOp(self, 'or', other)

    def prune(self, fields: list):
        data = self._prune(fields, self.to_dict())
        if data is INVALID:
            return None
        if data['l'] is INVALID:
            return BinaryOp.from_dict(data['r'])
        if data['r'] is INVALID:
            return BinaryOp.from_dict(data['l'])

        return BinaryOp.from_dict(data)

    def _prune(self, fields: list, data: dict):
        if isinstance(data['l'], dict):
            data['l'] = self._prune(fields, data['l'])
        elif isinstance(data['l'], str) and len(data['l']) > 2:
            prop = data['l']
            if '(' in prop:
                prop = self._remove_function_calls(prop)
            if prop.startswith('a:') and prop[2:] not in fields:
                return INVALID

        if isinstance(data['r'], dict):
            data['r'] = self._prune(fields, data['r'])
        elif isinstance(data['r'], str) and len(data['r']) > 2:
            prop = data['r']
            if '(' in prop:
                prop = self._remove_function_calls(prop)
            if prop.startswith('a:') and prop[2:] not in fields:
                return INVALID

        if data['l'] is INVALID and data['r'] is not INVALID:
            return data['r']
        if data['l'] is not INVALID and data['r'] is INVALID:
            return data['l']
        if data['l'] is INVALID and data['r'] is INVALID:
            return INVALID

        return data

    def to_sql(self, prefix: str = None):
        sql, params, counter = self._to_sql(prefix=prefix)
        return sql, params

    def _to_sql(self, counter: int = None, params: dict = None, prefix: str = None):
        counter = counter or 1
        params = params or {}
        rhv = None
        lhv, params, counter = self._process_op(self.lhv, params, counter, prefix=prefix)
        if self.op in ('is', 'is not'):
            if self.rhv == 'null' or self.rhv is None:
                rhv = 'null'
            elif self.rhv is False or self.rhv is True:
                rhv = str(self.rhv).lower()
        else:
            rhv, params, counter = self._process_op(self.rhv, params, counter, prefix=prefix)

        ret_op = self.op
        if ret_op == 'startswith':
            ret_op = 'like'
            rhv = f"CONCAT({rhv}, '%')"
        elif ret_op == 'endswith':
            ret_op = 'like'
            rhv = f"CONCAT('%', {rhv})"

        return f'({lhv} {ret_op.replace("==", "=")} {rhv})', params, counter

    @staticmethod
    def _process_op(v, params: dict, counter: int, prefix: str = None):
        if isinstance(v, BinaryOp):
            v, p, counter = v._to_sql(counter, params, prefix=prefix)
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
        elif isinstance(v, (Attr, AttributeString)) and prefix is not None:
            if isinstance(v, Attr):
                if not v.attr._value.startswith(f'{prefix}."'):
                    v.attr._value = f'{prefix}."{v.attr._value}"'
            else:
                if not v._value.startswith(f'{prefix}."'):
                    v._value = f'{prefix}."{v._value}"'

        return v, params, counter

    def __repr__(self):
        lhv = repr(self.lhv)
        rhv = repr(self.rhv)
        if lhv == '1' and rhv == '1' and self.op == '==':
            return T
        if lhv == T and rhv != T:
            return rhv
        if rhv == T and lhv != T:
            return lhv

        return f'({self.lhv} {self.op} {self.rhv})'.replace('==', '=')

    def __eq__(self, other):
        return isinstance(other, BinaryOp) and self.to_dict() == other.to_dict()
