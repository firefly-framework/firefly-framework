class Widget:
    name: str = 'foo'


class Repository:
    def __init__(self, type_):
        self.type_ = type_
        self.criteria = None

    def find_all_where(self, criteria):
        self.criteria = criteria
        return criteria


class Attr:
    def __init__(self, attr: str):
        self.attr = attr

    def is_none(self):
        return BinaryOp(self.attr, 'is', 'None')

    def is_false(self):
        return BinaryOp(self.attr, '==', False)

    def is_true(self):
        return BinaryOp(self.attr, '==', True)

    def __eq__(self, other):
        return BinaryOp(self.attr, '==', other)

    def __ne__(self, other):
        return BinaryOp(self.attr, '!=', other)

    def __contains__(self, item):
        print("CALLED")
        return BinaryOp(self.attr, 'in', item)


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


x = Repository(Widget).find_all_where((Attr('name') == 'foo') & ('foobar' in Attr('name')))

print(x)
