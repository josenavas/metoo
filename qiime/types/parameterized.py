from qiime.types import type_registry, Parameterized
from qiime.core.util import is_list

import qiime.types.primitives as p

@type_registry.parameterized
def Range(type_, min_, max_):
    _assert_valid_type(type_, [p.Integer, p.Decimal])
    _assert_valid_args(type_, [min_, max_])

    class Range(Parameterized):
        subtype = type_
        args = (min_, max_)

        @classmethod
        def normalize(cls, data):
            data = cls.subtype.normalize(data)

            if not (min_ <= data < max_):
                raise Exception()

            return data

    return Range

@type_registry.parameterized
def List(type_):
    class List(Parameterized):
        subtype = type_
        args = ()

        @classmethod
        def normalize(cls, data):
            if not is_list(data):
                data = (data,)
            return [cls.subtype.normalize(d) for d in data]

        @classmethod
        def load(cls, data):
            return [cls.subtype.load(d) for d in cls.normalize(data)]
    return List

@type_registry.parameterized
def ChooseOne(type_, options):
    _assert_valid_type(type_, [p.Integer, p.Decimal, p.String])
    _assert_valid_args(type_, options)

    class ChooseOne(Parameterized):
        subtype = type_
        args = options

        @classmethod
        def normalize(cls, data):
            data = cls.subtype.normalize(data)

            if data not in options:
                raise Exception()

            return data

    return ChooseOne

@type_registry.parameterized
def ChooseMany(type_, options):
    _assert_valid_type(type_, [p.Integer, p.Decimal, p.String])
    _assert_valid_args(type_, options)

    class ChooseMany(Parameterized):
        subtype = type_
        args = options

        @classmethod
        def normalize(cls, data):
            if not is_list(data):
                data = (data,)

            norm = []
            for d in data:
                d = cls.subtype.normalize(d)

                if d not in options:
                    raise Exception()
                norm.append(d)
            return norm

        @classmethod
        def load(cls, data):
            return [cls.subtype.load(d) for d in cls.normalize(data)]

    return ChooseMany

def _assert_valid_args(type_, args):
    for arg in args:
        type_.normalize(arg)

def _assert_valid_type(type_, valid_types):
    if not any(map(lambda x: issubclass(type_, x), valid_types)):
        raise TypeError("Invalid type %r." % type(type_))
