from __future__ import annotations

from typing import Union, List

import firefly.domain as ffd


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
            data = data.to_dict()

        return self._do_match(self, data)

    def _do_match(self, bop: BinaryOp, data: dict) -> bool:
        if isinstance(bop.lhv, BinaryOp):
            lhv = self._do_match(bop.lhv, data)
        elif isinstance(bop.lhv, AttributeString):
            lhv = data[bop.lhv]
        elif isinstance(bop.lhv, Attr):
            lhv = data[bop.lhv.attr]
        else:
            lhv = bop.lhv

        if isinstance(bop.rhv, BinaryOp):
            rhv = self._do_match(bop.rhv, data)
        elif isinstance(bop.rhv, AttributeString):
            rhv = data[bop.rhv]
        elif isinstance(bop.rhv, Attr):
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
            return lhv is rhv
        if bop.op == 'in':
            return lhv in rhv
        if bop.op == 'contains':
            return rhv in lhv
        if bop.op == 'and':
            return lhv and rhv
        if bop.op == 'or':
            return lhv or rhv

        raise ffd.LogicError(f"Don't know how to handle op: {bop.op}")

    def __and__(self, other):
        return BinaryOp(self, 'and', other)

    def __or__(self, other):
        return BinaryOp(self, 'or', other)

    def __repr__(self):
        return f'({self.lhv} {self.op} {self.rhv})'
