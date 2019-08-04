from __future__ import annotations


class AttributeString(str):
    pass


class Attr:
    def __init__(self, attr: str, default=None):
        self.attr = AttributeString(attr)
        self.default = default

    def is_none(self):
        return BinaryOp(self.attr, 'is', 'None')

    def is_false(self):
        return BinaryOp(self.attr, 'is', False)

    def is_true(self):
        return BinaryOp(self.attr, 'is', True)

    def is_in(self, set_):
        return BinaryOp(self.attr, 'in', set_)

    def contains(self, value):
        return BinaryOp(self.attr, 'contains', value)

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
        return self.default


class BinaryOp:
    def __init__(self, lhv, op, rhv):
        self.lhv = lhv
        self.op = op
        self.rhv = rhv

    def __and__(self, other):
        return BinaryOp(self, 'and', other)

    def __or__(self, other):
        return BinaryOp(self, 'or', other)

    def __repr__(self):
        return f'({self.lhv} {self.op} {self.rhv})'
